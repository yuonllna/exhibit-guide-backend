from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import os
import io
import qrcode
import boto3
from datetime import datetime
from app.services.llm.image_generator import ImageRegenService

router = APIRouter()
service = ImageRegenService()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads")
STATIC_ORIGINALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "references")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# S3 설정
S3_BUCKET_NAME = os.getenv("ARTWORK_S3_BUCKET_NAME")
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

@router.post("/artworks/regenerate-image")
async def regenerate_artwork_image(
    prompt: str = Form(""),
    original_filename: str = Form(...),
    user_image: UploadFile = File(...)
):
    try:
        user_image_path = os.path.join(UPLOAD_DIR, f"user_{user_image.filename}")
        original_image_path = os.path.join(STATIC_ORIGINALS_DIR, original_filename)

        if not os.path.exists(original_image_path):
            raise HTTPException(status_code=400, detail=f"원본 이미지 '{original_filename}'이 존재하지 않습니다.")

        with open(user_image_path, "wb") as f:
            f.write(await user_image.read())

        result_bytes = service.regenerate_image(user_image_path, original_image_path, prompt)

        if not result_bytes:
            raise HTTPException(status_code=500, detail="이미지 재생성 실패")

        # 업로드 파일명 생성
        result_filename = f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

        # S3 업로드
        s3_client.upload_fileobj(io.BytesIO(result_bytes), S3_BUCKET_NAME, result_filename, ExtraArgs={"ContentType": "image/png"})

        # 프리사인드 URL 생성
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': result_filename},
            ExpiresIn=3600  # 유효시간 (초 단위), 예: 1시간
        )

        return JSONResponse(content={"presigned_url": presigned_url})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {e}")

@router.post("/artworks/generate-qrcode")
async def generate_qrcode(image_url: str = Form(..., description="S3 업로드된 이미지 URL")):
    try:
        qr = qrcode.make(image_url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QR 코드 생성 실패: {e}")
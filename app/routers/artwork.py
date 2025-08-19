from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import os
import io
from app.services.llm.image_generator import ImageRegenService

router = APIRouter()

service = ImageRegenService()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

STATIC_ORIGINALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "originals")

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

        if result_bytes:
            return StreamingResponse(io.BytesIO(result_bytes), media_type="image/png")
        else:
            raise HTTPException(status_code=500, detail="이미지 재생성 실패")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {e}")

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import os
import io
from app.services.llm.image_generator import ImageRegenService


router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
service = ImageRegenService()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/artworks/regenerate-image")
async def regenerate_artwork_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),         
    size: str = Form("1024x1024")
):
    # 업로드 원본 이미지 저장
    image_path = os.path.join(UPLOAD_DIR, image.filename)
    with open(image_path, "wb") as f:
        f.write(await image.read())

    result_bytes = service.regenerate_image(image_path, prompt)

    if result_bytes:
        
        '''
        GENERATED_DIR = "generated"
        os.makedirs(GENERATED_DIR, exist_ok=True)
        from datetime import datetime
        save_name = (
            f"{os.path.splitext(image.filename)[0]}_regen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )
        save_path = os.path.join(GENERATED_DIR, save_name)
        with open(save_path, "wb") as f:
            f.write(result_bytes)
        print(f"저장 경로: {save_path}")
        '''

        return StreamingResponse(
            io.BytesIO(result_bytes),
            media_type="image/png"
        )
    else:
        raise HTTPException(status_code=500, detail="이미지 재생성 실패")

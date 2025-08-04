from fastapi import APIRouter, Path, Body, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from utils.qr import generate_qr_code

router = APIRouter()

class UserArtworkRequest(BaseModel):
    artifact_id: int
    image_url: str

class UserArtworkResponse(BaseModel):
    artwork_id: int
    user_id: int
    artifact_id: int
    image_url: str
    qr_code_url: Optional[str]
    created_at: datetime

@router.post(
    "/api/users/{user_id}/artworks",
    response_model=UserArtworkResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user_artwork(
    user_id: int = Path(...),
    data: UserArtworkRequest = Body(...)
):
    # QR 생성 예시
    qr_data = f"https://your-service.com/artworks/{user_id}"
    save_path = f"qr_codes/{user_id}_{data.artifact_id}.png"
    qr_code_url = generate_qr_code(qr_data, save_path)  # 실제 구현엔 S3 업로드 후 URL, DB저장 등 연동
    # DB 실제 저장 후 얻는 PK값
    artwork_id = 1
    created_at = datetime.now()
    return UserArtworkResponse(
        artwork_id=artwork_id,
        user_id=user_id,
        artifact_id=data.artifact_id,
        image_url=data.image_url,
        qr_code_url=qr_code_url,
        created_at=created_at
    )

import boto3
from fastapi import APIRouter, Query, Path, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models import Artifact, ArtifactExplanation
from app.database import get_db
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

router = APIRouter()

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
bucket_name = os.getenv("S3_BUCKET_NAME")

def generate_presigned_url(key: str) -> str:
    # key에 ".mp3"를 붙여서 완전한 파일 경로를 생성
    key_with_extension = f"{key}.mp3"  
    
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key_with_extension},
        ExpiresIn=3600  # URL 만료 시간 (1시간)
    )


class ArtifactListResponse(BaseModel):
    id: int = Field(..., alias="artifact_id")
    name: str
    image_url: str
    

@router.get("/galleries/{gallery_id}/artifacts", response_model=List[ArtifactListResponse])
def get_artifacts(
    gallery_id: int = Path(..., description="전시 ID"),
    db: Session = Depends(get_db)
):
    artifacts = db.query(Artifact).filter(Artifact.gallery_id == gallery_id).all()
    return artifacts


# ✅ 응답 모델 (오디오 제거)
class ArtifactExplanationResponse(BaseModel):
    artifact_name: str
    image_url: str
    explanation_text: str
    explanation_audio_url: str

# ✅ GET /api/artifacts/{artifact_id}/explanations
@router.get("/artifacts/{artifact_id}/explanations", response_model=List[ArtifactExplanationResponse])
def get_explanations(
    artifact_id: int = Path(..., description="유물 ID"),
    db: Session = Depends(get_db)
):
    artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
    if not artifact:
        return []

    explanations = db.query(ArtifactExplanation).filter(ArtifactExplanation.artifact_id == artifact_id).all()

    return [
        ArtifactExplanationResponse(
            artifact_name=artifact.name,
            image_url=artifact.image_url,
            explanation_text=e.explanation_text,
            explanation_audio_url=generate_presigned_url(e.explanation_audio_key) if e.explanation_audio_key else ""
        )
        for e in explanations
    ]
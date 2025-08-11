from fastapi import APIRouter, Query, Path
from typing import List, Optional
from pydantic import BaseModel
from app.models import Artifact, ArtifactExplanation  # 실제 ORM 모델 import

router = APIRouter()

class ArtifactListResponse(BaseModel):
    name: str
    image_url: str

@router.get("/api/artifacts", response_model=List[ArtifactListResponse])
async def get_artifacts(gallery_id: int = Query(...)):
    artifacts = await Artifact.filter(gallery_id=gallery_id).all()
    return [
        ArtifactListResponse(name=a.name, image_url=a.image_url)
        for a in artifacts
    ]

class ArtifactExplanationResponse(BaseModel):
    artifact_name: str
    image_url: str
    explanation_text: str
    explanation_audio_url: Optional[str] = None

@router.get("/api/artifacts/{artifact_id}/explanations", response_model=List[ArtifactExplanationResponse])
async def get_explanations(artifact_id: int = Path(...)):
    artifact = await Artifact.get(artifact_id=artifact_id)
    explanations = await ArtifactExplanation.filter(artifact_id=artifact_id).all()
    return [
        ArtifactExplanationResponse(
            artifact_name=artifact.name,
            image_url=artifact.image_url,
            explanation_text=e.explanation_text,
            explanation_audio_url=e.explanation_audio_url
        )
        for e in explanations
    ]

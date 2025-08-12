from fastapi import APIRouter, Path, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.models import FAQ, Artifact
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

# FAQ 응답 모델
class FAQResponse(BaseModel):
    faq_id: int
    question_text: str
    answer_text: str

# GET /api/artifacts/{artifact_id}/faqs
@router.get("/api/artifacts/{artifact_id}/faqs", response_model=List[FAQResponse])
def get_faqs(
    artifact_id: int = Path(..., description="유물 ID"),
    db: Session = Depends(get_db)
):
    artifact = db.query(Artifact).filter(Artifact.artifact_id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="유물을 찾을 수 없습니다")

    faqs = db.query(FAQ).filter(FAQ.artifact_id == artifact_id).all()
    
    return [
        FAQResponse(
            faq_id=faq.faq_id,
            question_text=faq.question_text,
            answer_text=faq.answer_text
        )
        for faq in faqs
    ]

# GET /api/faqs - 모든 FAQ 조회 (선택사항)
@router.get("/api/faqs", response_model=List[FAQResponse])
def get_all_faqs(db: Session = Depends(get_db)):
    faqs = db.query(FAQ).all()
    return [
        FAQResponse(
            faq_id=faq.faq_id,
            question_text=faq.question_text,
            answer_text=faq.answer_text
        )
        for faq in faqs
    ]

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Exhibition

router = APIRouter()

# Pydantic 스키마
class ExhibitionResponse(BaseModel):
    name: str
    image_url: str
    class Config:
        orm_mode = True

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/exhibitions", response_model=List[ExhibitionResponse])
def get_exhibitions(db: Session = Depends(get_db)):
    exhibitions = db.query(Exhibition).all()
    return exhibitions  # Pydantic이 orm_mode로 변환해줌

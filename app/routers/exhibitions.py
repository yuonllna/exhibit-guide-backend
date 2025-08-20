from pydantic import BaseModel, Field
from typing import List
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Exhibition

router = APIRouter()

class ExhibitionResponse(BaseModel):
    id: int = Field(..., alias="exhibition_id")
    name: str
    description: str
    image_url: str
    type: str

@router.get("/exhibitions", response_model=List[ExhibitionResponse])
def get_exhibitions(db: Session = Depends(get_db)):
    exhibitions = db.query(Exhibition).all()
    return exhibitions
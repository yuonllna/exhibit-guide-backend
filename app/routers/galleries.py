from fastapi import APIRouter, Path, HTTPException, Depends
from typing import List
from pydantic import BaseModel, Field
from app.models import Gallery
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

class GalleryResponse(BaseModel):
    id: int = Field(..., alias="gallery_id")
    name: str
    description: str
    image_url: str

@router.get("/api/exhibitions/{exhibition_id}/galleries", response_model=List[GalleryResponse])
def get_galleries(
    exhibition_id: int = Path(..., description="전시 ID"),
    db: Session = Depends(get_db)
):
    galleries = db.query(Gallery).filter(Gallery.exhibition_id == exhibition_id).all()
    return galleries

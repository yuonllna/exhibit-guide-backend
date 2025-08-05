from fastapi import APIRouter, Query
from typing import List
from pydantic import BaseModel
from app.models import Gallery  
router = APIRouter()

class GalleryResponse(BaseModel):
    name: str
    description: str
    image_url: str

@router.get("/api/galleries", response_model=List[GalleryResponse])
async def get_galleries(exhibition_id: int = Query(...)):
    galleries = await Gallery.filter(exhibition_id=exhibition_id).all()
    return [
        GalleryResponse(
            name=g.name,
            description=g.description,
            image_url=g.image_url
        )
        for g in galleries
    ]

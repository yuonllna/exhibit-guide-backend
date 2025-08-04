from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from models import Exhibition
router = APIRouter()

class ExhibitionResponse(BaseModel):
    name: str
    image_url: str

@router.get("/api/exhibitions", response_model=List[ExhibitionResponse])
async def get_exhibitions():
    exhibitions = await Exhibition.all()
    return [
        ExhibitionResponse(name=e.name, image_url=e.image_url)
        for e in exhibitions
    ]

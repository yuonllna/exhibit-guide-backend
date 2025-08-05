from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# routers 폴더 하위 모듈 임포트
from app.routers import exhibitions, galleries, artifacts, artworks

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(exhibitions.router)
app.include_router(galleries.router)
app.include_router(artifacts.router)
app.include_router(artworks.router)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

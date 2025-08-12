from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 임베딩/LLM 준비 ---
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.services.embedding.searcher import load_index
from app.services.llm.gemini_client import GeminiClient
from app.routers.qa import router as qa_router
from app.routers.onboarding import router as onboarding_router

# --- 도메인 라우터들 ---
from app.routers import exhibitions, galleries, artifacts, artworks, faq

app = FastAPI()

# CORS: 설정에서 읽고, 없으면 로컬 리액트만 허용(필요 시 추가)
allow_origins = getattr(settings, "cors_origins", ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.on_event("startup")
def startup():
    # 모델/인덱스/LLM 1회 로드
    app.state.encoder = SentenceTransformer(settings.model_name)
    app.state.index, app.state.documents = load_index(settings.faiss_dir)
    app.state.gemini = GeminiClient(api_key=settings.google_api_key)

# 공통 
app.include_router(qa_router, prefix="/api", tags=["qa"])
app.include_router(onboarding_router, prefix="/api", tags=["onboarding"])

# 도메인 라우터들 (각 라우터 내부에서 prefix를 이미 갖고 있으면 그대로 둡니다)
app.include_router(exhibitions.router)
app.include_router(galleries.router)
app.include_router(artifacts.router)
app.include_router(artworks.router)
app.include_router(faq.router)


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 서비스/모델 준비 ---
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.services.embedding.searcher import load_index
from app.services.llm.gemini_client import GeminiClient

# --- Router Import ---
from app.routers.qa import router as qa_router
from app.routers.onboarding import router as onboarding_router
from app.routers.artwork import router as artwork_router
from app.routers import exhibitions, galleries, artifacts
from app.routers.tts import router as tts_router

app = FastAPI()

# --- CORS 세팅 ---
allow_origins = getattr(settings, "cors_origins", ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 기본 Root API ---
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# --- Startup 이벤트 ---
@app.on_event("startup")
def startup():
    app.state.encoder = SentenceTransformer(settings.model_name)
    app.state.index, app.state.documents = load_index(settings.faiss_dir)
    app.state.gemini = GeminiClient()

# --- API Router 등록 ---
app.include_router(qa_router, prefix="/api", tags=["qa"])
app.include_router(onboarding_router, prefix="/api", tags=["onboarding"])
app.include_router(artwork_router, prefix="/api", tags=["artwork"])
app.include_router(tts_router, prefix="/api", tags=["tts"])

# --- 기타 서비스(전시, 미술관, 유물 등) 라우터 등록 ---
app.include_router(exhibitions.router, prefix="/api", tags=["exhibitions"])
app.include_router(galleries.router, prefix="/api", tags=["galleries"])
app.include_router(artifacts.router, prefix="/api", tags=["artifacts"])


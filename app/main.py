from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.services.embedding.searcher import load_index
from app.services.llm.gemini_client import GeminiClient
from app.routers.qa import router as qa_router

app = FastAPI()

@app.get("/")
def read_rood():
    return {"Hello": "World"}

@app.on_event("startup")
def startup():
    # 모델/인덱스/LLM 1회 로드
    app.state.encoder = SentenceTransformer(settings.model_name)
    app.state.index, app.state.documents = load_index(settings.faiss_dir)
    app.state.gemini = GeminiClient(api_key=settings.google_api_key)

app.include_router(qa_router, prefix="/api", tags=["qa"])


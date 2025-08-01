from fastapi import APIRouter, Depends, Request, HTTPException
from sentence_transformers import SentenceTransformer
import numpy as np

from app.schemas.qa import Question, Answer
from app.services.embedding.searcher import search
from app.services.llm.gemini_client import GeminiClient

router = APIRouter()

def get_encoder(request: Request) -> SentenceTransformer:
    return request.app.state.encoder

def get_index_docs(request: Request):
    return request.app.state.index, request.app.state.documents

def get_llm(request: Request) -> GeminiClient:
    return request.app.state.gemini

@router.post("/artifacts/{artifact_id}/questions", response_model=Answer)
def ask_question(
    artifact_id: str,
    q: Question,
    encoder: SentenceTransformer = Depends(get_encoder),
    idx_docs = Depends(get_index_docs),
    llm: GeminiClient = Depends(get_llm),
):
    index, documents = idx_docs

    # 1) 쿼리 임베딩
    q_vec = encoder.encode([q.question]).astype("float32")

    # 2) 전체 검색 후 해당 작품만 필터
    D, I = search(index, q_vec, k=50)  # 넉넉히 뽑기
    cand_indices = [i for i in I[0] if documents[i]["id"] == artifact_id]
    if not cand_indices:
        raise HTTPException(status_code=404, detail="No relevant passages for this artifact.")

    top_idx = cand_indices[0]
    doc = documents[top_idx]

    # 3) LLM 호출
    answer_text = llm.answer(doc["text"], q.question)

    return Answer(
        question=q.question,
        matched_text=doc["text"],
        artwork_id=doc["id"],
        gemini_answer=answer_text,
    )

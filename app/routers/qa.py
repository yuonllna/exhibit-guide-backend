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
    #artifact_id: str,
    q: Question,
    encoder: SentenceTransformer = Depends(get_encoder),
    idx_docs = Depends(get_index_docs),
    llm: GeminiClient = Depends(get_llm),
):
    index, documents = idx_docs

    # 1) 질문 임베딩
    q_vec = encoder.encode([q.question]).astype("float32")

    # 2) 상위 k개 문서 검색
    k = 3
    D, I = search(index, q_vec, k=k)

    # 3) 유사도 필터링 
    threshold = 0.4
    filtered_docs = [
        (documents[i], D[0][rank])
        for rank, i in enumerate(I[0])
        if D[0][rank] < threshold
    ]

    if not filtered_docs:
        raise HTTPException(status_code=404, detail="No sufficiently relevant passages.")

    # 4) 최대 3개만 선택
    top_docs = [doc for doc, _ in filtered_docs[:3]]

    # 5) 텍스트 합치기
    combined_text = "\n\n".join([f"- {doc['text']}" for doc in top_docs])

    # 6) Gemini 호출
    answer_text = llm.answer(combined_text, q.question)

    print("\n[🔍 Gemini RAG 검색 결과]")
    for i, doc in enumerate(top_docs):
        print(f"[{i+1}] ID: {doc['id']}")
        print(f"Text: {doc['text']}\n")

    return Answer(
        question=q.question,
        gemini_answer=answer_text,
    )

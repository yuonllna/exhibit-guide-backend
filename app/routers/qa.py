from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File
from sentence_transformers import SentenceTransformer
import numpy as np

from app.schemas.qa import Question, Answer
from app.services.speech.stt import SpeechToTextService
from app.services.embedding.searcher import search
from app.services.llm.gemini_client import GeminiClient

router = APIRouter()

def get_encoder(request: Request) -> SentenceTransformer:
    return request.app.state.encoder

def get_index_docs(request: Request):
    return request.app.state.index, request.app.state.documents

def get_llm(request: Request) -> GeminiClient:
    return request.app.state.gemini

@router.post("/artifacts/questions", response_model=Answer)
async def ask_question_by_voice(
    file: UploadFile = File(...),
    encoder: SentenceTransformer = Depends(get_encoder),
    idx_docs = Depends(get_index_docs),
    llm: GeminiClient = Depends(get_llm),
):
    index, documents = idx_docs

    # 1) 음성 파일 로드
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/webm"]:
        raise HTTPException(status_code=400, detail="WAV 또는 WebM 형식만 지원됩니다.")

    audio_content = await file.read()

    # 2) Google stt
    stt_service = SpeechToTextService()
    try:
        question_text = stt_service.transcribe(audio_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    print(f"[🎙️ STT 변환 결과] {question_text}")

    # 3) 질문 임베딩
    q_vec = encoder.encode([question_text]).astype("float32")

    # 4) 상위 k개 문서 검색
    k = 3
    D, I = search(index, q_vec, k=k)

    # 5) 유사도 필터링
    threshold = 0.5
    filtered_docs = [
        (documents[i], D[0][rank])
        for rank, i in enumerate(I[0])
        if D[0][rank] < threshold
    ]

    if not filtered_docs:
        print("[📭 유사한 문서 없음] 컨텍스트 없이 LLM 호출")
        answer_text = llm.answer("", question_text)
        print(answer_text)
        return Answer(
            question=question_text,
            gemini_answer=answer_text,
        )
    
    # 6) 최대 3개 문서 추출
    top_docs = [doc for doc, _ in filtered_docs[:3]]
    combined_text = "\n\n".join([f"- {doc['text']}" for doc in top_docs])

    # 7) Gemini 호출
    answer_text = llm.answer(combined_text, question_text)

    print("\n[🔍 Gemini RAG 검색 결과]")
    for i, doc in enumerate(top_docs):
        print(f"[{i+1}] ID: {doc['id']}")
        print(f"Text: {doc['text']}\n")

    return Answer(
        question=question_text,
        gemini_answer=answer_text,
    )
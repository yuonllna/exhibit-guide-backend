from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.stt.stt import SpeechToTextService
from app.utils.language import detect_language_by_charset 

router = APIRouter()

@router.post("/onboarding/detect-language")
async def detect_language_from_voice(file: UploadFile = File(...)):
    if file.content_type not in ["audio/wav", "audio/x-wav", "audio/webm"]:
        raise HTTPException(status_code=400, detail="지원되지 않는 음성 형식입니다.")

    audio_content = await file.read()
    stt_service = SpeechToTextService()

    try:
        transcript = stt_service.transcribe(audio_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT 실패: {str(e)}")

    try:
        lang_code = detect_language_by_charset(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"언어 판단 실패: {str(e)}")

    # db 저장

    return {
        "transcript": transcript,
        "language": lang_code
    }

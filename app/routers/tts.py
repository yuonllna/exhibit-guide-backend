from fastapi import APIRouter, HTTPException, Body, Depends, Request
from fastapi.responses import StreamingResponse
from datetime import datetime
import io, os

from app.schemas.tts import TTSRequest, AudioEncoding
from app.services.speech.tts import TextToSpeechService

router = APIRouter(tags=["tts"])

def get_tts(request: Request) -> TextToSpeechService:
    svc = getattr(request.app.state, "tts", None)
    if svc is None:
        key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcloud-key.json")
        svc = TextToSpeechService(key_path)
        request.app.state.tts = svc
    return svc

@router.post("/tts/synthesize")
async def tts_synthesize(
    payload: TTSRequest = Body(...),
    tts: TextToSpeechService = Depends(get_tts),
):
    try:
        audio = tts.synthesize(
            text=payload.text,
            language_code=payload.language_code,
            voice_name=payload.voice_name,
            speaking_rate=payload.speaking_rate,
            pitch=payload.pitch,
            audio_encoding=payload.audio_encoding.value,  
            ssml=payload.ssml,
            sample_rate_hz=payload.sample_rate_hz,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # MIME/확장자 결정
    if payload.audio_encoding is AudioEncoding.MP3:
        media, ext = "audio/mpeg", "mp3"
    elif payload.audio_encoding is AudioEncoding.LINEAR16:
        media, ext = "audio/wav", "wav"
    else:
        media, ext = "audio/ogg", "ogg"

    filename = f"tts_{payload.language_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return StreamingResponse(
        io.BytesIO(audio),
        media_type=media,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )

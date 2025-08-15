from fastapi import APIRouter, HTTPException, Body, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from google.oauth2 import service_account
from google.cloud import texttospeech as gtts
import io, os
from datetime import datetime

router = APIRouter(tags=["tts"])

class TextToSpeechService:
    def __init__(self, key_path: str = "gcloud-key.json"):
        creds = service_account.Credentials.from_service_account_file(key_path)
        self.client = gtts.TextToSpeechClient(credentials=creds)

    def synthesize(
        self,
        text: str,
        language_code: str = "ko-KR",
        voice_name: str | None = None,
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        audio_encoding: str = "OGG_OPUS",  # "MP3" | "OGG_OPUS" | "LINEAR16"
        ssml: bool = False,
        sample_rate_hz: int | None = 48000,  # None이면 기본값
    ) -> bytes:
        if not text:
            raise ValueError("text is empty")

        synth_input = gtts.SynthesisInput(ssml=text) if ssml else gtts.SynthesisInput(text=text)

        voice_kwargs = {"language_code": language_code}
        if voice_name:
            voice_kwargs["name"] = voice_name
        voice = gtts.VoiceSelectionParams(**voice_kwargs)

        enc_map = {
            "MP3": gtts.AudioEncoding.MP3,
            "OGG_OPUS": gtts.AudioEncoding.OGG_OPUS,
            "LINEAR16": gtts.AudioEncoding.LINEAR16,
        }
        audio_cfg = gtts.AudioConfig(
            audio_encoding=enc_map.get(audio_encoding.upper(), gtts.AudioEncoding.OGG_OPUS),
            speaking_rate=speaking_rate,
            pitch=pitch,
            sample_rate_hertz=sample_rate_hz if sample_rate_hz else None,
        )

        resp = self.client.synthesize_speech(input=synth_input, voice=voice, audio_config=audio_cfg)
        if not resp or not resp.audio_content:
            raise RuntimeError("TTS synth failed")
        return resp.audio_content


_tts = TextToSpeechService(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcloud-key.json"))

class TTSRequest(BaseModel):
    text: str = Field(..., description="읽어줄 텍스트(또는 SSML)")
    language_code: str = "ko-KR"
    voice_name: str | None = None            # 예: "ko-KR-Wavenet-B"
    speaking_rate: float = 1.0               # 0.25~4.0
    pitch: float = 0.0                        # -20.0~20.0
    audio_encoding: str = "OGG_OPUS"          # "MP3" | "OGG_OPUS" | "LINEAR16"
    ssml: bool = False
    sample_rate_hz: int | None = 48000

@router.post("/tts/synthesize")
async def tts_synthesize(payload: TTSRequest = Body(...)):
    try:
        audio = _tts.synthesize(
            text=payload.text,
            language_code=payload.language_code,
            voice_name=payload.voice_name,
            speaking_rate=payload.speaking_rate,
            pitch=payload.pitch,
            audio_encoding=payload.audio_encoding,
            ssml=payload.ssml,
            sample_rate_hz=payload.sample_rate_hz,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 포맷별 MIME과 확장자
    enc = payload.audio_encoding.upper()
    if enc == "MP3":
        media, ext = "audio/mpeg", "mp3"
    elif enc == "LINEAR16":
        media, ext = "audio/wav", "wav"   # LINEAR16은 WAV 컨테이너로 반환
    else:
        media, ext = "audio/ogg", "ogg"

    filename = f"tts_{payload.language_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return StreamingResponse(
        io.BytesIO(audio),
        media_type=media,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )

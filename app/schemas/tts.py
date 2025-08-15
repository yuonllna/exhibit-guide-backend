from pydantic import BaseModel, Field, conint, confloat, constr
from enum import Enum
from typing import Optional

class AudioEncoding(str, Enum):
    MP3 = "MP3"
    OGG_OPUS = "OGG_OPUS"
    LINEAR16 = "LINEAR16"

class TTSRequest(BaseModel):
    text: constr(min_length=1) = Field(..., description="읽어줄 텍스트(또는 SSML)")
    language_code: constr(min_length=2) = "ko-KR"
    voice_name: Optional[str] = None
    speaking_rate: confloat(ge=0.25, le=4.0) = 1.0
    pitch: confloat(ge=-20.0, le=20.0) = 0.0
    audio_encoding: AudioEncoding = AudioEncoding.OGG_OPUS
    ssml: bool = False
    sample_rate_hz: Optional[conint(ge=8000, le=48000)] = 48000

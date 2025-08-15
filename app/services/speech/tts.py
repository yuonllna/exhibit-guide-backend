from google.oauth2 import service_account
from google.cloud import texttospeech as tts

class TextToSpeechService:
    def __init__(self, key_path: str = "gcloud-key.json"):
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = tts.TextToSpeechClient(credentials=credentials)

    def synthesize(
        self,
        text: str,
        language_code: str = "ko-KR",
        voice_name: str | None = None,              # 예: "ko-KR-Wavenet-B"
        ssml: bool = False,                         # SSML 사용 시 True
        speaking_rate: float = 1.0,                 # 0.25 ~ 4.0
        pitch: float = 0.0,                         # -20.0 ~ 20.0 (semitones)
        audio_encoding: str = "OGG_OPUS",           # "MP3", "LINEAR16", "OGG_OPUS"
    ) -> bytes:
        if not text:
            raise ValueError("text가 비어 있습니다.")

        # 입력 (텍스트 또는 SSML)
        synthesis_input = tts.SynthesisInput(ssml=text) if ssml else tts.SynthesisInput(text=text)

        # 보이스 선택
        voice_params = dict(language_code=language_code)
        if voice_name:
            voice_params["name"] = voice_name
        voice = tts.VoiceSelectionParams(**voice_params)

        # 오디오 설정
        encoding_map = {
            "MP3": tts.AudioEncoding.MP3,
            "LINEAR16": tts.AudioEncoding.LINEAR16,
            "OGG_OPUS": tts.AudioEncoding.OGG_OPUS,
        }
        audio_config = tts.AudioConfig(
            audio_encoding=encoding_map.get(audio_encoding.upper(), tts.AudioEncoding.OGG_OPUS),
            speaking_rate=speaking_rate,
            pitch=pitch,
            sample_rate_hertz=48000,  # STT와 맞추려면 48k 추천
        )

        # 합성
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        if not response or not response.audio_content:
            raise RuntimeError("TTS 합성에 실패했습니다.")

        return response.audio_content

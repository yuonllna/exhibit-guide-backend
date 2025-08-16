from google.oauth2 import service_account
from google.cloud import texttospeech as gtts

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
        sample_rate_hz: int | None = 48000,
    ) -> bytes:
        if not text:
            raise ValueError("text is empty")

        synthesis_input = gtts.SynthesisInput(ssml=text) if ssml else gtts.SynthesisInput(text=text)

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

        resp = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_cfg
        )
        if not resp or not resp.audio_content:
            raise RuntimeError("TTS synth failed")
        return resp.audio_content

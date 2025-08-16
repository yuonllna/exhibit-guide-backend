from google.oauth2 import service_account
from google.cloud import speech_v1p1beta1 as speech

class SpeechToTextService:
    def __init__(self, key_path: str = "gcloud-key.json"):
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.client = speech.SpeechClient(credentials=credentials)

    def transcribe(self, audio_content: bytes) -> str:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="ko-KR",
            alternative_language_codes=["en-US", "ja-JP", "zh-CN"]
        )

        response = self.client.recognize(config=config, audio=audio)

        if not response.results:
            raise ValueError("음성을 인식하지 못했습니다.")

        return response.results[0].alternatives[0].transcript

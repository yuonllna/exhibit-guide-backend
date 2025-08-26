from dotenv import load_dotenv
from google.genai import Client
import os

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = Client(api_key=api_key)
        self.model_name = model_name

    def answer(self, context: str, question: str) -> str:
        prompt = (
            "당신은 미술 작품에 대해 설명해주는 전문가입니다.\n\n"
            f"다음은 미술 작품에 대한 설명입니다:\n\"\"\"{context}\"\"\"\n\n"
            f"사용자의 질문:\n\"\"\"{question}\"\"\"\n\n"
            "만약 위의 설명이 충분하지 않더라도, 당신이 알고 있는 일반적인 예술 지식과 맥락을 바탕으로 "
            "친절하고 이해하기 쉽게 대답해주세요."
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt],
                config={"response_modalities": ["TEXT"]},
            )
            if response.candidates and response.candidates[0].content.parts:
                answer = ""
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "text") and part.text:
                        answer += part.text
                return answer.strip()
            return ""
        except Exception as e:
            print(f"[ERROR] QA 응답 실패: {e}")
            return ""

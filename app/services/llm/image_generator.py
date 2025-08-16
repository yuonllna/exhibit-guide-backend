from dotenv import load_dotenv
from google.genai import Client, types
import os

load_dotenv()

class ImageRegenService:
    def __init__(self, model_name: str = "gemini-2.0-flash-preview-image-generation"):
        self.client = Client()
        self.model_name = model_name

    def regenerate_image(self, image_path: str, prompt: str) -> bytes:
        try:
            if not prompt:
                prompt = "기존의 작품에 새로운 그림을 추가한 이미지입니다. 이를 그림체를 통일하여 자연스럽게 재생성해주세요."

            with open(image_path, "rb") as f:
                image_bytes = f.read()
            contents = [
                prompt,
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png"
                )
            ]

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={"response_modalities": ["IMAGE", "TEXT"]}
            )
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    return part.inline_data.data
            print("[ERROR] 결과에 이미지 데이터 없음")
            return None
        except Exception as e:
            print(f"[ERROR] 이미지 재생성 실패: {e}")
            return None

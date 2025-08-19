from dotenv import load_dotenv
from google.genai import Client, types
import os

load_dotenv()

class ImageRegenService:
    def __init__(self, model_name: str = "gemini-2.0-flash-preview-image-generation"):
        self.client = Client()
        self.model_name = model_name

    def regenerate_image(self, user_image_path: str, original_image_path: str, prompt: str = "") -> bytes:
        try:
            if not prompt:
                prompt = (
                    "첫 번째 이미지는 사용자가 추가로 그린 그림이고, 두 번째 이미지는 원래의 작품입니다. "
                    "두 이미지를 조화롭게 통합하여 자연스럽고 통일된 스타일로 재창조된 그림을 생성해주세요."
                )

            # 이미지 파일 열기
            with open(user_image_path, "rb") as f:
                user_image_bytes = f.read()
            with open(original_image_path, "rb") as f:
                original_image_bytes = f.read()

            # 프롬프트와 두 이미지 전달
            contents = [
                prompt,
                types.Part.from_bytes(data=user_image_bytes, mime_type="image/png"),
                types.Part.from_bytes(data=original_image_bytes, mime_type="image/png"),
            ]

            # Gemini 호출
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={"response_modalities": ["IMAGE", "TEXT"]}
            )

            # 결과 이미지 추출
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data is not None:
                    return part.inline_data.data

            print("[ERROR] 결과에 이미지 없음")
            return None

        except Exception as e:
            print(f"[ERROR] 이미지 재생성 실패: {e}")
            return None

import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def answer(self, context: str, question: str) -> str:
        prompt = f"""당신은 미술 작품에 대해 설명해주는 전문가입니다.

다음은 미술 작품에 대한 설명입니다:
\"\"\"{context}\"\"\"

사용자의 질문:
\"\"\"{question}\"\"\"

위의 설명과 질문을 바탕으로 친절하게 대답해주세요."""
        resp = self.model.generate_content(prompt)
        return getattr(resp, "text", "").strip()

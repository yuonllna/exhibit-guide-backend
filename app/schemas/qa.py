from pydantic import BaseModel

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    question: str
    matched_text: str
    artwork_id: str
    gemini_answer: str

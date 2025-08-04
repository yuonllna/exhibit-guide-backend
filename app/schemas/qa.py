from pydantic import BaseModel

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    question: str
    gemini_answer: str

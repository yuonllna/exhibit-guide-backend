import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# .env 파일에서 환경변수 불러오기
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 동기 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# FastAPI dependency로 사용할 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

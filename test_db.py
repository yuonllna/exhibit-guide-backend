import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# .env 파일 로드
load_dotenv()

# 환경 변수에서 DB URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# 동기용 SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print("PostgreSQL 버전:", version[0])

if __name__ == "__main__":
    test_connection()

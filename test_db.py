import asyncio
from app.database import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def test_connection():
    async with AsyncSession(engine) as session:
        # 단순 쿼리(예: PostgreSQL 버전 확인)
        result = await session.execute(text("SELECT version();"))
        version = result.fetchone()
        print("PostgreSQL 버전:", version[0])

if __name__ == "__main__":
    asyncio.run(test_connection())

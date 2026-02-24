import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def test_db():
    db_url = os.getenv("DATABASE_URL")
    if db_url.startswith("postgres://"):
        db_url = "postgresql+asyncpg://" + db_url[len("postgres://"):]
    elif db_url.startswith("postgresql://"):
        db_url = "postgresql+asyncpg://" + db_url[len("postgresql://"):]
    
    print(f"Testing DB: {db_url.split('@')[-1]}")
    try:
        engine = create_async_engine(db_url)
        async with engine.connect() as conn:
            res = await conn.execute(text("SELECT 1"))
            print(f"DB Result: {res.scalar()}")
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())

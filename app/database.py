import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# 1. Ensure the protocol is correct for asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgresql://"):]

# 2. Extract SSL settings from the URL if present, then strip them
# asyncpg is picky about the URL structure
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

# 3. Create a proper SSL context for cloud providers like Neon/Render
# This is the most robust way to handle "sslmode=require" in asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 4. Create Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": ssl_context}, # Correct way for asyncpg
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print(f"DATABASE ERROR: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

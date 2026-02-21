import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Robust protocol replacement
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgresql://"):]

# Manually handle query parameters to avoid urlparse/urlunparse issues with custom protocols
connect_args = {}
base_url = DATABASE_URL
if "?" in DATABASE_URL:
    base_url, query_string = DATABASE_URL.split("?", 1)
    params = parse_qs(query_string)
    
    # Handle sslmode
    if "sslmode" in params:
        ssl_mode = params["sslmode"][0]
        if ssl_mode in ["require", "verify-ca", "verify-full"]:
            connect_args["ssl"] = True
    
    # Remove incompatible params for asyncpg
    # We reconstruct the URL without any query params to stay safe
    DATABASE_URL = base_url

# Log masked URL for debugging without exposing secrets
masked_url = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL
print(f"DEBUG: Connecting to host: {masked_url}")

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    connect_args=connect_args
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
        finally:
            await session.close()

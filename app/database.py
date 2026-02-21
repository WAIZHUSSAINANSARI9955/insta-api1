import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Strip potential quotes and whitespace (fixes common copy-paste issues on cloud platforms)
DATABASE_URL = DATABASE_URL.strip().strip("'").strip('"')

# Ensure the URL starts with postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# asyncpg doesn't support 'sslmode'. We need to move it to 'connect_args' as 'ssl'
parsed_url = urlparse(DATABASE_URL)
query_params = parse_qs(parsed_url.query)

connect_args = {}
if "sslmode" in query_params:
    ssl_mode = query_params.pop("sslmode")[0]
    # asyncpg uses 'ssl' instead of 'sslmode'
    if ssl_mode in ["require", "verify-ca", "verify-full"]:
        connect_args["ssl"] = True
    else:
        connect_args["ssl"] = False

# Remove other potential incompatible arguments for asyncpg
query_params.pop("channel_binding", None)

# Reconstruct the URL without the problematic query parameters
new_query = urlencode(query_params, doseq=True)
DATABASE_URL = urlunparse(parsed_url._replace(query=new_query))

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

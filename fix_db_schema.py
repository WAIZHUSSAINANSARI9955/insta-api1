import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

async def fix_db():
    db_url = os.getenv("DATABASE_URL")
    if db_url.startswith("postgres://"):
        db_url = "postgresql+asyncpg://" + db_url[len("postgres://"):]
    elif db_url.startswith("postgresql://"):
        db_url = "postgresql+asyncpg://" + db_url[len("postgresql://"):]
    
    # Simple SSL fix for asyncpg
    if "sslmode" in db_url:
        db_url = db_url.split("?")[0]

    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    print(f"Connecting to DB to add 'biography' column...")
    try:
        engine = create_async_engine(db_url, connect_args={"ssl": ctx})
        async with engine.begin() as conn:
            # Try to add biography column if it doesn't exist
            try:
                await conn.execute(text("ALTER TABLE users ADD COLUMN biography TEXT;"))
                print("✅ Successfully added 'biography' column.")
            except Exception as e:
                if "already exists" in str(e):
                    print("ℹ️ Column 'biography' already exists.")
                else:
                    print(f"❌ Error adding column: {e}")
            
            # Also ensure followers_count etc are correct
            # Sometime if they were added later they might be missing too
    except Exception as e:
        print(f"DB Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_db())

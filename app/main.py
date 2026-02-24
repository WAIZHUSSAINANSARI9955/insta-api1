import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .database import engine, Base
from .routes import profile, media

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Instagram Scraping API",
    description="Production-ready FastAPI system for Instagram scraping and bulk downloading.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Permissive CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust startup
@app.on_event("startup")
async def startup():
    logger.info("Starting up and checking database connection...")
    try:
        async with engine.begin() as conn:
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database connection and table check SUCCESSFUL.")
    except Exception as e:
        logger.error(f"DATABASE STARTUP FAILED: {e}")
        # We don't exit, but this helps the user see the log

# Include routes
app.include_router(profile.router)
app.include_router(media.router)

@app.get("/")
async def root(request: Request):
    return {
        "status": "online",
        "message": "Instagram API is running",
        "endpoints": ["/profile/{username}", "/media/{username}"]
    }

if __name__ == "__main__":
    # Ensure uvicorn runs on 8000 and clears previous binds if possible
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

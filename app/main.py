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
import traceback
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Instagram Scraping API",
    description="Production-ready FastAPI system for Instagram scraping and bulk downloading.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"GLOBAL ERROR: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "traceback": traceback.format_exc()},
    )

# Permissive CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup logic
@app.on_event("startup")
async def startup():
    logger.info("Local Backend Ready at http://localhost:8000")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"DB Error: {e}")

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

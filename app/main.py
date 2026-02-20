import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .database import engine, Base
from .routes import profile, media

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Instagram Scraping API",
    description="Production-ready FastAPI system for Instagram scraping and bulk downloading.",
    version="1.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # This will create tables if they don't exist
        # In a real production app, use Alembic migrations
        await conn.run_sync(Base.metadata.create_all)

# Include routes
app.include_router(profile.router)
app.include_router(media.router)

@app.get("/")
@limiter.limit("5/minute")
async def root(request: Request):
    return {
        "message": "Welcome to Instagram Scraping API",
        "docs": "/docs",
        "endpoints": {
            "profile": "/profile/{username}",
            "media": "/media/{username}",
            "bulk_download": "/bulk-download/{username} (POST)"
        }
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

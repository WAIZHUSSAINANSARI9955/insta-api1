# Instagram Scraping API

A production-ready FastAPI system for scraping Instagram profiles and bulk downloading media.

## Features
- **Profile Scraping**: Fetch followers, following, posts count, and profile details.
- **Media Categorization**: Distinguishes between posts, videos, and reels.
- **Database Caching**: Scraped data is cached for 6 hours to reduce redundant requests.
- **Bulk Downloading**: Asynchronously download all media and stream as a ZIP file.
- **Security**: Rate limiting, environment secret management, and input validation.
- **Async Architecture**: Built with `httpx`, `FastAPI`, and `SQLAlchemy (async)`.

## Project Structure
```text
app/
 ├── main.py            # API Entry point & Middleware
 ├── database.py        # SQLAlchemy Async Engine
 ├── models.py          # PostgreSQL Tables (User, Media, Download)
 ├── schemas.py         # Pydantic Schemas
 ├── services/
 │     ├── scraper.py    # Instagram Scraping Logic
 │     ├── downloader.py # ZIP creation & File downloading
 ├── routes/
 │     ├── profile.py    # Profile endpoints
 │     ├── media.py      # Media & Bulk download endpoints
 ├── utils/
 │     ├── helpers.py    # Random headers & Delays
```

## Setup & Local Development

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd insta-api
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file (copied from `.env.example`):
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_kNUI8VzcMjf2@ep-proud-hat-aipjeqfx-pooler.c-4.us-east-1.aws.neon.tech/insta-api?sslmode=require
```

### 5. Run the Application
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Swagger docs: `http://localhost:8000/docs`.

## API Endpoints

- **GET `/profile/{username}`**: Fetch profile data (cached for 6h).
- **GET `/media/{username}`**: List all media items for a previously scraped user.
- **POST `/bulk-download/{username}`**: Download all user media as a ZIP file.

## Deployment on Render

1. **Create a New Web Service**:
   - Connect your GitHub repository.
   - Set **Runtime** to `Python 3`.
   - **Build Command**: `pip install -r requirements.txt`.
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

2. **Environment Variables**:
   - Add `DATABASE_URL` with your Neon PostgreSQL connection string. 
   - Ensure it starts with `postgresql+asyncpg://`.

3. **Database**:
   - The app automatically creates tables on startup using `Base.metadata.create_all` (async).

## Scraping Notice
This scraper uses `httpx` and `BeautifulSoup`. Instagram's public pages are volatile. If you encounter blocks, consider:
- Rotating Proxies.
- Using a headless browser (Playwright/Selenium) if JSON data becomes inaccessible via direct GET.
- Using official Instagram Graph API for higher reliability.

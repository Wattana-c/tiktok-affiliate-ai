# TikTok Affiliate AI Auto Content Machine 🚀

A scalable, production-ready affiliate automation system that fetches trending products, generates viral multi-variant AI content (Bilingual: Thai & English), and schedules multi-account auto-posting with smart fallback and rate limiting.

## 🏗 System Architecture

1. **Scraping Engine**: Fetches trending products and assigns a calculated `trend_score`.
2. **Smart Decision Engine**: Uses `trend_score` to decide actions:
   - **Score >= 80**: Automates posting queue.
   - **Score >= 50 and < 80**: Places in 'review' queue.
   - **Score < 50**: Skips content generation.
3. **AI Content Generator**: Generates multiple A/B variants (`soft_sell`, `hard_sell`, `problem_solution`) concurrently using OpenAI. Enforces natural, native-level Thai or high-energy English. Includes a "Smart Mock" fallback if the OpenAI API key is not provided.
4. **Celery Worker Pipeline**: Manages asynchronous stages and retries.
   - `Scrape` -> `Generate Variants` -> `Queue` -> `Post`
   - Includes exponential backoff and max retry limits.
5. **Multi-Account Auto-Poster**: Supports tracking `rate_limit` per account. Auto-disables accounts after 5 consecutive failed posts to protect the system.
6. **React Admin Dashboard**: Built with Vite + Tailwind CSS. Manages queue review, visualizes AI variants, links social accounts, and provides global statistics.

## 🛠 Prerequisites

- Docker & Docker Compose
- (Optional but recommended) OpenAI API Key to utilize the actual GPT models.

## 🚀 Setup & Run Instructions

### 1. Environment Setup

Clone the repository and set up your environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file and input your `OPENAI_API_KEY`. (If left blank, the system will use a smart mock generator which simulates outputs for testing).

### 2. Start Services

Use the provided script to start the PostgreSQL database, Redis, FastAPI Backend, Celery Worker, and React Frontend.

```bash
./run.sh
```
*Note: If you do not want to use the script, you can run `docker-compose up --build -d` directly.*

### 3. Database Migrations

Apply the database schema and models for the backend:
```bash
docker-compose exec backend alembic upgrade head
```

### 4. Access the Dashboard

- **Frontend Admin Panel**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Running Tests

To run the local backend test suite (API and Celery logic testing):
```bash
cd backend
python -m pip install -r requirements.txt pytest httpx
PYTHONPATH=. pytest tests/
```

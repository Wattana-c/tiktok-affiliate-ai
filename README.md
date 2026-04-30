# TikTok Affiliate AI Auto Content Machine 🚀

A scalable, production-ready affiliate automation system that fetches trending products, generates viral multi-variant AI content (Bilingual: Thai & English), tracks conversion metrics, and schedules multi-account auto-posting with smart fallback and rate limiting. This architecture forms an end-to-end **Growth Optimization Engine**.

## 🏗 System Architecture & Growth Engine

1. **Robust TikTok Data Ingestion**: A hybrid pipeline (API -> Scraper -> Mock) utilizing rotating User-Agents and request throttling to safely extract real TikTok trends and map them to actionable product data.
2. **Smart Decision Engine**: Uses weighted algorithms mapping engagement rate and view velocity to a dynamic `trend_score`:
   - **Score >= 80**: High confidence. Auto-generates content and bypasses human review into the auto-post queue.
   - **Score >= 50 and < 80**: Med confidence. AI content is generated but flagged for manual admin `review`.
   - **Score < 50**: Low confidence. Skipped completely.
3. **Exploration vs Exploitation AI Strategy (80/20)**: Generates 3 A/B variants for each product. The AI algorithm allocates an 80% probability to reusing historically best-performing `content_mode`s (e.g. `soft_sell`, `hard_sell`, `problem_solution`), and a 20% probability of experimenting with new hooks. High-performing older hooks are ingested as few-shot prompt examples dynamically.
4. **Celery Worker Pipeline**: Manages asynchronous stages and retries.
   - Includes exponential backoff, maximum retry limits, and smart per-account daily rate limiting (spam avoidance).
5. **Multi-Account Auto-Poster**: Tracks API/Platform failures. Auto-disables an account after 5 consecutive failed posts.
6. **Performance Feedback Loop**: Real-time webhook APIs ingest views, clicks, and conversion data to weight and rank strategy successes in the database.
7. **React Admin Dashboard**: Built with Vite + Tailwind CSS. Track conversion rates, visually compare AI variants, approve the review queue, and configure system thresholds.

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

markdown
# Number Search Bot

Telegram bot that searches a phone number across ~850 parquet files
hosted on Hugging Face, using a JSON range index + DuckDB.

## Setup

1. Clone repo
2. `cp .env.example .env` and fill values
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

## Endpoints

- `GET /` — health + file count
- `GET /health` — ping
- `GET /search?number=XXXXXXXXXX` — direct test
- `POST /webhook/{secret}` — Telegram webhook

## Deploy on Render

- Push to GitHub
- Render → New Web Service → connect repo
- Set env vars (see `.env.example`)
- Deploy

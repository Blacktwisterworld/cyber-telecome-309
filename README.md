# Number Search Bot

Telegram bot that searches a phone number across ~850 parquet files
hosted on Hugging Face, using a JSON range index + DuckDB.

## Local Setup

1. `cp .env.example .env` and fill values
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload --port 8000`

For webhook testing locally, use ngrok:
`ngrok http 8000` and put the https URL in WEBHOOK_URL.

## Endpoints

- `GET /` — health + file count
- `GET /health` — ping
- `GET /search?number=XXXXXXXXXX` — direct test
- `POST /webhook/{secret}` — Telegram webhook

## Deploy on Render

1. Push repo to GitHub
2. Render → New Web Service → connect repo
3. Runtime: Docker
4. Set env vars (see `.env.example`)
5. Deploy

Set up a cron-job.org ping every 10 minutes to `/health` to avoid sleep.

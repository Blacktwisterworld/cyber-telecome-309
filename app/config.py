python
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "changeme").strip()
HF_DATASET_URL = os.getenv("HF_DATASET_URL", "").strip().rstrip("/")
PORT = int(os.getenv("PORT", "8000"))

# Validate on startup
def validate():
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if not WEBHOOK_URL:
        missing.append("WEBHOOK_URL")
    if not HF_DATASET_URL:
        missing.append("HF_DATASET_URL")
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

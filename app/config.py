import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip().rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "changeme").strip()
HF_DATASET_URL = os.getenv(
    "HF_DATASET_URL",
    "https://huggingface.co/datasets/Cyber-insight-309/Phone-1/resolve/main",
).strip().rstrip("/")
RANGES_URL = os.getenv(
    "RANGES_URL",
    "https://raw.githubusercontent.com/Blacktwisterworld/cyber-telecome-309/main/data/file_ranges.json",
).strip()
PORT = int(os.getenv("PORT", "8000"))


def validate():
    """
    Only TELEGRAM_TOKEN is required.
    HF_DATASET_URL has a default.
    WEBHOOK_URL is optional — app starts without it, webhook set later.
    """
    missing = []
    if not TELEGRAM_TOKEN:
        missing.append("TELEGRAM_TOKEN")
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

python
import re
import html
import httpx
from app.config import TELEGRAM_TOKEN
from app.search import find_record

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

_NUM_RE = re.compile(r"^\d{10,13}$")


async def _send_message(chat_id: int, text: str):
    async with httpx.AsyncClient(timeout=30) as client:
        await client.post(
            f"{TG_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
        )


def _format_record(result: dict, number: str) -> str:
    if result["status"] == "no_range_match":
        return f"❌ Number <code>{html.escape(number)}</code> kisi bhi file range me nahi mila."

    if result["status"] == "not_found":
        return (
            f"❌ Record nahi mila.\n"
            f"Number: <code>{html.escape(number)}</code>\n"
            f"Checked files: {result['tried']}"
        )

    rec = result["record"] or {}
    lines = [
        f"✅ <b>Record mil gaya</b>",
        f"Number: <code>{html.escape(number)}</code>",
        f"File: <code>{html.escape(result['file'])}</code>",
        f"Checked: {result['tried']} file(s)",
        "",
        "<b>Data:</b>",
    ]
    for k, v in rec.items():
        safe_v = html.escape(str(v)) if v is not None else "—"
        lines.append(f"• <b>{html.escape(k)}</b>: <code>{safe_v}</code>")

    return "\n".join(lines)


async def process_update(update: dict):
    """Handle one Telegram update object."""
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return

    chat_id = msg["chat"]["id"]
    text = (msg.get("text") or "").strip()

    if not text:
        return

    # /start or /help
    if text.startswith("/start") or text.startswith("/help"):
        await _send_message(
            chat_id,
            "👋 Number bhejo (10–13 digits). Main record dhoondh ke bataunga.",
        )
        return

    if not _NUM_RE.match(text):
        await _send_message(chat_id, "⚠️ Sirf 10–13 digit ka number bhejo.")
        return

    await _send_message(chat_id, "🔎 Search ho raha hai...")

    try:
        result = find_record(text)
        reply = _format_record(result, text)
    except Exception as e:
        print(f"[bot] error: {e}")
        reply = "⚠️ Server error. Baad me try karo."

    await _send_message(chat_id, reply)

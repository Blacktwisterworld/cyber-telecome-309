from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import httpx

from app import config
from app.bot import process_update
from app.search import find_record, get_candidates
from app.ranges import total_files, reload_ranges

app = FastAPI(title="Number Search Bot")


@app.on_event("startup")
async def _startup():
    config.validate()

    webhook_full = f"{config.WEBHOOK_URL}/webhook/{config.WEBHOOK_SECRET}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/setWebhook",
            json={"url": webhook_full, "drop_pending_updates": True},
        )
        print("[startup] setWebhook:", r.status_code, r.text)

    print(f"[startup] Loaded {total_files()} file ranges.")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "files_indexed": total_files(),
        "bot": "running",
    }


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/webhook/{secret}")
async def webhook(secret: str, request: Request, bg: BackgroundTasks):
    if secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")

    update = await request.json()
    bg.add_task(process_update, update)
    return JSONResponse({"ok": True})


@app.get("/search")
async def search(number: str):
    if not number or not number.isdigit():
        raise HTTPException(status_code=400, detail="invalid number")

    candidates = get_candidates(number)
    result = find_record(number)

    return {
        "number": number,
        "candidates_count": len(candidates),
        "candidates": candidates,
        "result": result,
    }


@app.post("/reload-ranges")
async def reload_ranges_endpoint(secret: str):
    """Call after updating JSON on GitHub: /reload-ranges?secret=xxx"""
    if secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")
    count = reload_ranges()
    return {"ok": True, "files_loaded": count}

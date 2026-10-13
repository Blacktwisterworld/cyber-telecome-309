import os
import json
from pathlib import Path
from functools import wraps

from flask import Flask, jsonify, request

app = Flask(__name__)

API_KEY = os.getenv("API_KEY", "")
RANGES_FILE = Path(
    os.getenv("RANGES_FILE", "file_ranges.json")
)


def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        supplied_key = request.headers.get("X-API-Key", "")

        if not API_KEY or supplied_key != API_KEY:
            return jsonify({
                "success": False,
                "error": "Unauthorized"
            }), 401

        return func(*args, **kwargs)

    return wrapper


def load_ranges():
    with RANGES_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    entries = data.get("files")

    if not isinstance(entries, list):
        raise ValueError(
            "JSON must contain a 'files' list"
        )

    return entries


def validate_ranges(entries):
    valid = 0
    invalid = 0

    for item in entries:
        if not isinstance(item, dict):
            invalid += 1
            continue

        first = str(item.get("first", ""))
        last = str(item.get("last", ""))
        filename = item.get("file")

        if (
            isinstance(filename, str)
            and filename
            and first.isdigit()
            and last.isdigit()
            and len(first) == len(last)
        ):
            valid += 1
        else:
            invalid += 1

    return {
        "total": len(entries),
        "valid": valid,
        "invalid": invalid,
    }


@app.get("/")
def home():
    return jsonify({
        "service": "Dataset Index Validator",
        "status": "running"
    })


@app.get("/index-status")
@require_api_key
def index_status():
    try:
        entries = load_ranges()
        report = validate_ranges(entries)

        return jsonify({
            "success": True,
            "index": report
        })

    except (OSError, ValueError, json.JSONDecodeError):
        app.logger.exception("Index validation failed")

        return jsonify({
            "success": False,
            "error": "Could not validate index"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )

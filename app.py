import os
import json
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Environment variables
API_KEY = os.getenv("API_KEY", "")
RANGES_FILE = os.getenv("RANGES_FILE", "file_ranges.json")


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
    with open(RANGES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("files", [])


def find_candidate_files(number, ranges):
    candidates = []

    for item in ranges:
        first = str(item.get("first", ""))
        last = str(item.get("last", ""))

        if not (
            number.isdigit()
            and first.isdigit()
            and last.isdigit()
            and len(number) == len(first) == len(last)
        ):
            continue

        low, high = sorted((first, last))

        if low <= number <= high:
            candidates.append(item.get("file"))

    return [name for name in candidates if name]


@app.get("/")
def home():
    return jsonify({
        "service": "Dataset Range Lookup API",
        "status": "running"
    })


@app.get("/lookup")
@require_api_key
def lookup():
    number = request.args.get("number", "").strip()

    if not number.isdigit() or len(number) != 10:
        return jsonify({
            "success": False,
            "error": "Enter a valid 10-digit number"
        }), 400

    try:
        ranges = load_ranges()
        candidates = find_candidate_files(number, ranges)

        return jsonify({
            "success": True,
            "candidate_count": len(candidates),
            "candidate_files": candidates,
            "message": (
                "Candidate files identified. "
                "Exact search can run against an authorized dataset."
            )
        })

    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "Range index file not found"
        }), 500

    except (json.JSONDecodeError, OSError) as exc:
        app.logger.error("Range index error: %s", exc)
        return jsonify({
            "success": False,
            "error": "Could not read range index"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )

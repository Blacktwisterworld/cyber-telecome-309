import json
import os
from typing import List, Dict

import httpx

from app.config import RANGES_URL

_LOCAL_JSON = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "file_ranges.json"
)


def _parse_ranges(data: dict) -> List[Dict]:
    ranges = []
    for item in data.get("files", []):
        try:
            first = int(item["first"])
            last = int(item["last"])
            lo, hi = (first, last) if first <= last else (last, first)
            ranges.append({"file": item["file"], "lo": lo, "hi": hi})
        except (ValueError, KeyError) as e:
            print(f"[ranges] skipping {item.get('file')}: {e}")
    return ranges


def _load_from_remote() -> List[Dict]:
    try:
        r = httpx.get(RANGES_URL, timeout=30, follow_redirects=True)
        r.raise_for_status()
        data = json.loads(r.text)
        ranges = _parse_ranges(data)
        if ranges:
            print(f"[ranges] loaded {len(ranges)} from remote")
            return ranges
    except Exception as e:
        print(f"[ranges] remote failed: {e}")
    return []


def _load_from_local() -> List[Dict]:
    try:
        if os.path.exists(_LOCAL_JSON):
            with open(_LOCAL_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            ranges = _parse_ranges(data)
            print(f"[ranges] loaded {len(ranges)} from local file")
            return ranges
        print(f"[ranges] local file not found: {_LOCAL_JSON}")
    except Exception as e:
        print(f"[ranges] local failed: {e}")
    return []


def _load_ranges() -> List[Dict]:
    ranges = _load_from_remote()
    if not ranges:
        ranges = _load_from_local()
    if not ranges:
        print("[ranges] WARNING: no ranges loaded")
    return ranges


_RANGES: List[Dict] = _load_ranges()


def reload_ranges() -> int:
    global _RANGES
    _RANGES = _load_ranges()
    return len(_RANGES)


def get_candidate_files(number: str) -> List[str]:
    try:
        num = int(number)
    except (ValueError, TypeError):
        return []
    return [r["file"] for r in _RANGES if r["lo"] <= num <= r["hi"]]


def total_files() -> int:
    return len(_RANGES)

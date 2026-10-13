import json
from typing import List, Dict

import httpx

from app.config import RANGES_URL


def _load_ranges() -> List[Dict]:
    """Fetch file_ranges.json from GitHub and build an int-based index."""
    try:
        r = httpx.get(RANGES_URL, timeout=30, follow_redirects=True)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[ranges] failed to fetch {RANGES_URL}: {e}")
        return []

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


_RANGES: List[Dict] = _load_ranges()


def reload_ranges() -> int:
    """Force re-fetch (useful if the JSON updates)."""
    global _RANGES
    _RANGES = _load_ranges()
    return len(_RANGES)


def get_candidate_files(number: str) -> List[str]:
    """Return parquet paths whose numeric range contains `number`."""
    try:
        num = int(number)
    except (ValueError, TypeError):
        return []

    return [r["file"] for r in _RANGES if r["lo"] <= num <= r["hi"]]


def total_files() -> int:
    return len(_RANGES)

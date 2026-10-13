python
import json
import os
from typing import List, Dict

RANGES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "file_ranges.json")

# Load once at import time
with open(RANGES_FILE, "r", encoding="utf-8") as f:
    _DATA = json.load(f)

# Pre-process: convert to int once so we don't do it on every query
_RANGES: List[Dict] = []
for item in _DATA["files"]:
    try:
        first = int(item["first"])
        last = int(item["last"])
        lo, hi = (first, last) if first <= last else (last, first)
        _RANGES.append({
            "file": item["file"],
            "lo": lo,
            "hi": hi,
        })
    except (ValueError, KeyError) as e:
        # Skip malformed entries
        print(f"[ranges] skipping {item.get('file')}: {e}")


def get_candidate_files(number: str) -> List[str]:
    """
    Return list of parquet file paths whose numeric range contains the number.
    Handles descending ranges and mixed-length numbers.
    """
    try:
        num = int(number)
    except ValueError:
        return []

    candidates = []
    for r in _RANGES:
        if r["lo"] <= num <= r["hi"]:
            candidates.append(r["file"])
    return candidates


def total_files() -> int:
    return len(_RANGES)

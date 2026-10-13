import duckdb
from functools import lru_cache
from typing import Optional, Dict

from app.config import HF_DATASET_URL
from app.ranges import get_candidate_files

# Single reusable DuckDB connection with httpfs for reading parquet over HTTP
_con = duckdb.connect()
_con.execute("INSTALL httpfs;")
_con.execute("LOAD httpfs;")
_con.execute("SET enable_progress_bar=false;")


# ---- Sensitive columns ko chhod ke sirf ye fields user ko dikhenge ----
SAFE_COLUMNS = ["mobile", "circle", "id"]


def _search_one_file(file_path: str, number: str) -> Optional[Dict]:
    """Search a single parquet file over HTTP via DuckDB."""
    url = f"{HF_DATASET_URL}/{file_path}"
    try:
        rows = _con.execute(
            f"""
            SELECT {', '.join(SAFE_COLUMNS)}
            FROM read_parquet('{url}')
            WHERE CAST(mobile AS VARCHAR) = ?
            LIMIT 1
            """,
            [number],
        ).fetchdf()

        if rows.empty:
            return None

        raw = rows.iloc[0].to_dict()
        cleaned = {}
        for k, v in raw.items():
            if v is None:
                continue
            s = str(v)
            if s == "nan" or s.strip() == "":
                continue
            cleaned[str(k)] = s
        return cleaned

    except Exception as e:
        print(f"[search] {file_path} failed: {e}")
        return None


@lru_cache(maxsize=500)
def find_record(number: str) -> Optional[Dict]:
    """
    Main entry:
      1. Get candidate files from range index.
      2. Search them one-by-one; return on first match.
    """
    number = number.strip()
    candidates = get_candidate_files(number)

    if not candidates:
        return {
            "status": "no_range_match",
            "file": None,
            "record": None,
            "tried": 0,
        }

    tried = 0
    for f in candidates:
        tried += 1
        rec = _search_one_file(f, number)
        if rec is not None:
            return {
                "status": "found",
                "file": f,
                "record": rec,
                "tried": tried,
            }

    return {
        "status": "not_found",
        "file": None,
        "record": None,
        "tried": tried,
    }


def get_candidates(number: str):
    return get_candidate_files(number)

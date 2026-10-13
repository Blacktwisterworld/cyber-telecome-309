python
import duckdb
from functools import lru_cache
from typing import Optional, Dict

from app.config import HF_DATASET_URL
from app.ranges import get_candidate_files

# ---- DuckDB connection (reuse across requests) ----
_con = duckdb.connect()
_con.execute("INSTALL httpfs;")
_con.execute("LOAD httpfs;")
# Optional: tune for low-memory env
_con.execute("SET enable_progress_bar=false;")


def _search_one_file(file_path: str, number: str) -> Optional[Dict]:
    """Search a single parquet file on Hugging Face via DuckDB HTTP."""
    url = f"{HF_DATASET_URL}/{file_path}"
    try:
        rows = _con.execute(
            f"""
            SELECT * FROM read_parquet('{url}')
            WHERE CAST(number AS VARCHAR) = ?
            LIMIT 1
            """,
            [number],
        ).fetchdf()

        if rows.empty:
            return None

        record = rows.iloc[0].to_dict()
        # Clean up NaN / None
        cleaned = {}
        for k, v in record.items():
            if v is None:
                continue
            if isinstance(v, float) and v != v:  # NaN
                continue
            cleaned[str(k)] = str(v)
        return cleaned

    except Exception as e:
        print(f"[search] {file_path} failed: {e}")
        return None


@lru_cache(maxsize=500)
def find_record(number: str) -> Optional[Dict]:
    """
    Main entry point:
    - get candidate files from range index
    - search sequentially, return on first match
    """
    number = number.strip()
    candidates = get_candidate_files(number)

    if not candidates:
        return {"status": "no_range_match", "file": None, "record": None, "tried": 0}

    tried = 0
    for f in candidates:
        tried += 1
        rec = _search_one_file(f, number)
        if rec is not None:
            return {"status": "found", "file": f, "record": rec, "tried": tried}

    return {"status": "not_found", "file": None, "record": None, "tried": tried}


def get_candidates(number: str):
    return get_candidate_files(number)

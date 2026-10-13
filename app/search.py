import os
import duckdb
from functools import lru_cache
from typing import Optional, Dict

from app.ranges import get_candidate_files

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HF_REPO = "Cyber-insight-309/Phone-1"

_con = duckdb.connect()
_con.execute("INSTALL httpfs;")
_con.execute("LOAD httpfs;")
_con.execute("SET enable_progress_bar=false;")

if HF_TOKEN:
    try:
        _con.execute(f"CREATE OR REPLACE SECRET hf_token (TYPE huggingface, TOKEN '{HF_TOKEN}');")
        print("[search] HF token secret configured ✓")
    except Exception as e:
        print(f"[search] HF token secret failed: {e}")

SAFE_COLUMNS = ["mobile", "circle", "id"]


def _build_url(file_path: str) -> str:
    fp = file_path.lstrip("/")
    return f"hf://datasets/{HF_REPO}/{fp}"


def _search_one_file(file_path: str, number: str) -> Optional[Dict]:
    url = _build_url(file_path)
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
        return {str(k): str(v) for k, v in raw.items() if v is not None and str(v) not in ("", "nan")}
    except Exception as e:
        print(f"[search] {file_path} failed: {e}")
        return None


@lru_cache(maxsize=500)
def find_record(number: str) -> Optional[Dict]:
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


# ---- DEBUG ----
def debug_file(file_path: str, number: str = None):
    url = _build_url(file_path)
    out = {"url": url, "file": file_path}
    try:
        schema_df = _con.execute(f"DESCRIBE SELECT * FROM read_parquet('{url}')").fetchdf()
        out["schema"] = schema_df.to_dict(orient="records")

        sample_df = _con.execute(f"SELECT * FROM read_parquet('{url}') LIMIT 3").fetchdf()
        out["sample"] = sample_df.to_dict(orient="records")

        cnt = _con.execute(f"SELECT COUNT(*) FROM read_parquet('{url}')").fetchone()[0]
        out["total_rows"] = int(cnt)

        if number:
            like_df = _con.execute(
                f"SELECT * FROM read_parquet('{url}') WHERE CAST(mobile AS VARCHAR) LIKE ? LIMIT 5",
                [f"%{number}%"],
            ).fetchdf()
            out["like_rows"] = len(like_df)
            out["like_data"] = like_df.to_dict(orient="records")
    except Exception as e:
        out["error"] = str(e)
    return out

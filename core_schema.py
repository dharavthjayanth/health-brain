"""
The canonical schema: the ONE format every data source must be translated into.

    person_id | date | metric | value | unit | source

Everything above the adapters (memory, baseline, patterns, ...) only ever sees
this shape. 'source' is provenance only; no layer may change its behaviour
based on it.
"""
import pandas as pd

COLUMNS = ["person_id", "date", "metric", "value", "unit", "source"]


def validate(df: pd.DataFrame) -> pd.DataFrame:
    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Adapter output is missing columns: {sorted(missing)}")
    out = df[COLUMNS].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out

"""
LAYER 1: MEMORY

Job: remember every measurement, permanently, in one clean format.

Rules this layer enforces
  1. Everything is stored as person / date / metric / value / unit / source.
  2. Adding the same data twice never creates duplicates (a day is a day).
  3. If the source later corrects a value, the new value wins, but the old
     one is written to a `corrections` table. Nothing silently disappears.
  4. Each person's memories are kept apart: recall("hari") can never
     return another person's rows.

This layer does NO thinking: no averages, no patterns. Only remembering.
"""
import os
import sqlite3
import sys
from datetime import datetime, timezone

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_schema import validate  # noqa: E402

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    person_id    TEXT NOT NULL,
    date         TEXT NOT NULL,
    metric       TEXT NOT NULL,
    value        REAL,
    unit         TEXT,
    source       TEXT,
    first_seen   TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    PRIMARY KEY (person_id, date, metric)
);
CREATE TABLE IF NOT EXISTS corrections (
    person_id TEXT, date TEXT, metric TEXT,
    old_value REAL, new_value REAL, changed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_person_metric ON observations (person_id, metric, date);
"""


class Memory:
    def __init__(self, path: str = "brain.db"):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def remember(self, long_df: pd.DataFrame) -> dict:
        """Store rows. Safe to call again with overlapping data."""
        df = validate(long_df)
        now = datetime.now(timezone.utc).isoformat()
        added = updated = unchanged = 0
        cur = self.conn.cursor()
        for r in df.itertuples(index=False):
            day = r.date.strftime("%Y-%m-%d")
            val = None if pd.isna(r.value) else float(r.value)
            row = cur.execute(
                "SELECT value FROM observations WHERE person_id=? AND date=? AND metric=?",
                (r.person_id, day, r.metric)).fetchone()
            if row is None:
                cur.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)",
                            (r.person_id, day, r.metric, val, r.unit, r.source, now, now))
                added += 1
            elif row[0] is not None and val is not None and abs(row[0] - val) > 1e-9:
                cur.execute("INSERT INTO corrections VALUES (?,?,?,?,?,?)",
                            (r.person_id, day, r.metric, row[0], val, now))
                cur.execute("UPDATE observations SET value=?, last_updated=? "
                            "WHERE person_id=? AND date=? AND metric=?",
                            (val, now, r.person_id, day, r.metric))
                updated += 1
            else:
                unchanged += 1
        self.conn.commit()
        return {"added": added, "updated": updated, "unchanged": unchanged}

    def recall(self, person_id: str) -> pd.DataFrame:
        """Everything remembered about ONE person, in the canonical schema."""
        df = pd.read_sql_query(
            "SELECT person_id, date, metric, value, unit, source FROM observations "
            "WHERE person_id=? ORDER BY date, metric", self.conn, params=(person_id,))
        df["date"] = pd.to_datetime(df["date"])
        return df

    def summary(self, person_id: str) -> dict:
        cur = self.conn.cursor()
        rows, first, last, days = cur.execute(
            "SELECT COUNT(*), MIN(date), MAX(date), COUNT(DISTINCT date) "
            "FROM observations WHERE person_id=?", (person_id,)).fetchone()
        metrics = cur.execute("SELECT COUNT(DISTINCT metric) FROM observations WHERE person_id=?",
                              (person_id,)).fetchone()[0]
        corrections = cur.execute("SELECT COUNT(*) FROM corrections WHERE person_id=?",
                                  (person_id,)).fetchone()[0]
        return {"rows": rows, "days": days, "metrics": metrics,
                "first_day": first, "last_day": last, "corrections": corrections}

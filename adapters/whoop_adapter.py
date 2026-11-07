"""
WHOOP adapter: translates WHOOP's four export CSVs into the canonical schema.

This is the ONLY file in the project allowed to know WHOOP's column names.
If WHOOP changes its export, only this file changes.
"""
import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_schema import validate  # noqa: E402

# WHOOP column -> (our metric name, unit)
CYCLE_FIELDS = {
    "Recovery score %": ("recovery", "%"),
    "Resting heart rate (bpm)": ("rhr", "bpm"),
    "Heart rate variability (ms)": ("hrv", "ms"),
    "Skin temp (celsius)": ("skin_temp", "C"),
    "Blood oxygen %": ("spo2", "%"),
    "Day Strain": ("day_strain", "au"),
    "Energy burned (cal)": ("energy_burned", "cal"),
    "Sleep performance %": ("sleep_performance", "%"),
    "Respiratory rate (rpm)": ("resp_rate", "rpm"),
    "Asleep duration (min)": ("sleep_min", "min"),
    "In bed duration (min)": ("in_bed_min", "min"),
    "Light sleep duration (min)": ("light_sleep_min", "min"),
    "Deep (SWS) duration (min)": ("deep_sleep_min", "min"),
    "REM duration (min)": ("rem_min", "min"),
    "Awake duration (min)": ("awake_min", "min"),
    "Sleep need (min)": ("sleep_need_min", "min"),
    "Sleep debt (min)": ("sleep_debt_min", "min"),
    "Sleep efficiency %": ("sleep_efficiency", "%"),
    "Sleep consistency %": ("sleep_consistency", "%"),
}


def _day(series):
    return pd.to_datetime(series).dt.strftime("%Y-%m-%d")


def load(person_id: str, folder: str) -> pd.DataFrame:
    parts = []

    # --- body + sleep metrics, one value per day ---
    pc = pd.read_csv(os.path.join(folder, "physiological_cycles.csv"))
    pc["date"] = _day(pc["Cycle start time"])
    for raw, (metric, unit) in CYCLE_FIELDS.items():
        if raw not in pc.columns:
            continue
        s = pc.groupby("date")[raw].mean().dropna()  # a few days have 2 cycles: average them
        parts.append(pd.DataFrame({"person_id": person_id, "date": s.index, "metric": metric,
                                   "value": s.values, "unit": unit, "source": "whoop"}))

    # --- workouts: roll up to daily load ---
    wo = pd.read_csv(os.path.join(folder, "workouts.csv"))
    wo["date"] = _day(wo["Cycle start time"])
    daily = wo.groupby("date").agg(workout_strain_total=("Activity Strain", "sum"),
                                   workout_min_total=("Duration (min)", "sum"),
                                   workout_count=("Activity Strain", "count"))
    for col, unit in [("workout_strain_total", "au"), ("workout_min_total", "min"), ("workout_count", "count")]:
        parts.append(pd.DataFrame({"person_id": person_id, "date": daily.index, "metric": col,
                                   "value": daily[col].values, "unit": unit, "source": "whoop"}))

    # --- journal: yes/no -> 1/0, only questions with real variance ---
    je = pd.read_csv(os.path.join(folder, "journal_entries.csv"))
    je["date"] = _day(je["Cycle start time"])
    je["yes"] = je["Answered yes"].astype(str).str.lower().eq("true").astype(int)
    piv = je.pivot_table(index="date", columns="Question text", values="yes", aggfunc="max")
    for q in piv.columns:
        v = piv[q].dropna()
        # keep only if asked on >=15 days with >=3 yes and >=3 no; else it is noise, not a variable
        if len(v) >= 15 and v.sum() >= 3 and (len(v) - v.sum()) >= 3:
            name = "journal:" + q.lower().replace("?", "").strip().replace(" ", "_")
            parts.append(pd.DataFrame({"person_id": person_id, "date": v.index, "metric": name,
                                       "value": v.values, "unit": "bool", "source": "whoop_journal"}))

    return validate(pd.concat(parts, ignore_index=True))

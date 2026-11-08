"""
LAYER 2: NORMAL

Job: work out what is typical for ONE person, using only that person's own history.

For every metric this layer reports
  * overall    : how many days, average, typical range (middle half of days), wide range
  * contexts   : the same metric on weekdays vs weekends, higher- vs lower-strain days,
                 longer- vs shorter-sleep nights (each side shows its own number of days)
  * recent     : the last 14 days vs everything before them, judged against the
                 person's own day-to-day variability

Honesty rules (hard requirements)
  * Fewer than MIN_DAYS_BASELINE days of a metric -> "not enough data yet", no numbers.
  * A comparison group with fewer than MIN_GROUP_N days -> "not enough data yet".
  * Days with no reading are simply absent. They are never filled in or guessed.
  * One person per call. Mixing people raises an error.
  * No population norms anywhere. "Normal" always means normal for THIS person.
"""
import numpy as np
import pandas as pd

MIN_DAYS_BASELINE = 5
MIN_GROUP_N = 8
RECENT_DAYS = 14
LOAD_METRIC = "day_strain"      # splits days into higher- vs lower-strain
SLEEP_METRIC = "sleep_min"      # splits nights into longer vs shorter sleep
NOT_ENOUGH = "not enough data yet"


def to_daily(long_df: pd.DataFrame) -> pd.DataFrame:
    """Canonical long table -> one row per day, one column per metric."""
    people = long_df["person_id"].unique()
    if len(people) != 1:
        raise ValueError(f"Layer 2 works on exactly one person at a time, got {list(people)}")
    wide = long_df.pivot_table(index="date", columns="metric", values="value", aggfunc="mean")
    wide.index = pd.to_datetime(wide.index)
    return wide.sort_index()


def describe(s: pd.Series):
    s = s.dropna()
    if len(s) < MIN_DAYS_BASELINE:
        return {"status": NOT_ENOUGH, "n": int(len(s))}
    return {
        "status": "ok", "n": int(len(s)),
        "mean": round(float(s.mean()), 1), "median": round(float(s.median()), 1),
        "std": round(float(s.std()), 1),
        "min": round(float(s.min()), 1), "max": round(float(s.max()), 1),
        "typical_low": round(float(s.quantile(0.25)), 1),    # middle half of days
        "typical_high": round(float(s.quantile(0.75)), 1),
        "wide_low": round(float(s.quantile(0.10)), 1),       # middle 80% of days
        "wide_high": round(float(s.quantile(0.90)), 1),
    }


def _compare(a: pd.Series, b: pd.Series, label_a: str, label_b: str):
    a, b = a.dropna(), b.dropna()
    if len(a) < MIN_GROUP_N or len(b) < MIN_GROUP_N:
        return {"status": NOT_ENOUGH, label_a + "_n": int(len(a)), label_b + "_n": int(len(b))}
    return {"status": "ok",
            label_a: round(float(a.mean()), 1), label_a + "_n": int(len(a)),
            label_b: round(float(b.mean()), 1), label_b + "_n": int(len(b))}


def contexts(daily: pd.DataFrame, metric: str):
    out = {}
    s = daily[metric]
    weekend = daily.index.dayofweek >= 5
    out["weekday_vs_weekend"] = _compare(s[~weekend], s[weekend], "weekday", "weekend")
    for splitter, name, hi, lo in [(LOAD_METRIC, "higher_vs_lower_strain", "higher_strain", "lower_strain"),
                                   (SLEEP_METRIC, "longer_vs_shorter_sleep", "longer_sleep", "shorter_sleep")]:
        if splitter in daily.columns and metric != splitter:
            sp = daily[splitter]
            med = sp.median()
            high = s[(sp >= med)]
            low = s[(sp < med)]
            out[name] = _compare(high, low, hi, lo)
    return out


def recent_vs_earlier(s: pd.Series, overall: dict):
    s = s.dropna()
    if overall.get("status") != "ok" or s.empty:
        return {"status": NOT_ENOUGH}
    cutoff = s.index.max() - pd.Timedelta(days=RECENT_DAYS - 1)
    recent, earlier = s[s.index >= cutoff], s[s.index < cutoff]
    if len(recent) < MIN_GROUP_N or len(earlier) < MIN_GROUP_N:
        return {"status": NOT_ENOUGH, "recent_n": int(len(recent)), "earlier_n": int(len(earlier))}
    diff = float(recent.mean() - earlier.mean())
    # "about the same" is judged against this person's own day-to-day swing
    if overall["std"] and abs(diff) < 0.5 * overall["std"]:
        direction = "about the same"
    else:
        direction = "higher" if diff > 0 else "lower"
    return {"status": "ok", "window_days": RECENT_DAYS,
            "recent_mean": round(float(recent.mean()), 1), "recent_n": int(len(recent)),
            "earlier_mean": round(float(earlier.mean()), 1), "earlier_n": int(len(earlier)),
            "difference": round(diff, 1), "direction": direction,
            "window": f"{cutoff.date()} to {s.index.max().date()}"}


def compute_normal(long_df: pd.DataFrame) -> dict:
    daily = to_daily(long_df)
    metrics = {}
    for m in daily.columns:
        if str(m).startswith("journal:"):      # yes/no answers are not a "normal range"
            continue
        overall = describe(daily[m])
        entry = {"overall": overall}
        if overall["status"] == "ok":
            entry["contexts"] = contexts(daily, m)
            entry["recent"] = recent_vs_earlier(daily[m], overall)
        metrics[m] = entry
    first, last = daily.index.min(), daily.index.max()
    span = (last - first).days + 1
    return {
        "person_id": str(long_df["person_id"].iloc[0]),
        "data_range": {"first_day": str(first.date()), "last_day": str(last.date()),
                       "days_with_data": int(len(daily)), "calendar_days": int(span),
                       "days_missing": int(span - len(daily))},
        "metrics": metrics,
    }


def render(normal: dict, metric: str) -> str:
    """Plain-words summary of one metric. Describes computed numbers only."""
    e = normal["metrics"].get(metric)
    if e is None:
        return f"No {metric} data for {normal['person_id']}."
    o = e["overall"]
    if o["status"] != "ok":
        return f"{metric}: {NOT_ENOUGH} ({o['n']} days)."
    lines = [f"{metric}: average {o['mean']}, usually between {o['typical_low']} and {o['typical_high']} "
             f"(middle half of {o['n']} days); on 8 of 10 days between {o['wide_low']} and {o['wide_high']}."]
    for name, c in e.get("contexts", {}).items():
        if c["status"] != "ok":
            lines.append(f"  {name.replace('_', ' ')}: {NOT_ENOUGH}.")
            continue
        keys = [k for k in c if k != "status" and not k.endswith("_n")]
        a, b = keys
        lines.append(f"  {a.replace('_', ' ')} {c[a]} (n={c[a + '_n']}) vs {b.replace('_', ' ')} {c[b]} (n={c[b + '_n']})")
    r = e.get("recent", {})
    if r.get("status") == "ok":
        verdict = ("about the same as usual for them" if r["direction"] == "about the same"
                   else f"{r['direction']} than usual for them")
        lines.append(f"  last {r['window_days']} days ({r['recent_n']} had a reading): {r['recent_mean']} vs "
                     f"{r['earlier_mean']} before (n={r['earlier_n']}), {verdict}.")
    return "\n".join(lines)

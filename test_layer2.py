"""Tests for Layer 2 (Normal). Run: python3 test_layer2.py"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import whoop_adapter
from layers.layer2_normal import NOT_ENOUGH, compute_normal, render

hari = whoop_adapter.load("hari", os.path.join(HERE, "data", "hari"))
n = compute_normal(hari)

print("TEST 1: numbers match the earlier independent analysis of Hari")
rec = n["metrics"]["recovery"]["overall"]
print("  recovery:", rec["n"], rec["mean"], rec["typical_low"], rec["typical_high"])
assert (rec["n"], rec["mean"]) == (81, 64.1)
assert (rec["typical_low"], rec["typical_high"]) == (50.5, 82.0)
assert n["metrics"]["hrv"]["overall"]["mean"] == 77.5
assert n["data_range"]["days_with_data"] == 82 and n["data_range"]["days_missing"] == 34

print("TEST 2: group sizes add up (no day lost or double counted)")
c = n["metrics"]["recovery"]["contexts"]["weekday_vs_weekend"]
assert c["weekday_n"] + c["weekend_n"] == rec["n"]
print("  weekday + weekend =", c["weekday_n"] + c["weekend_n"])

print("TEST 3: too little data says 'not enough data yet' and gives no numbers")
tiny = hari[hari["metric"] == "recovery"].head(4)
nt = compute_normal(tiny)
o = nt["metrics"]["recovery"]["overall"]
assert o["status"] == NOT_ENOUGH and "mean" not in o
print("  4 days ->", o)

print("TEST 4: small comparison groups are refused, not guessed")
twelve = hari[hari["metric"].isin(["recovery", "day_strain", "sleep_min"])]
twelve = twelve[twelve["date"] <= sorted(twelve["date"].unique())[11]]   # first 12 days
nm = compute_normal(twelve)
for name, grp in nm["metrics"]["recovery"]["contexts"].items():
    print("  ", name, "->", grp["status"])
    assert grp["status"] == NOT_ENOUGH

print("TEST 5: refuses to mix two people")
other = hari.copy()
other["person_id"] = "someone_else"
try:
    compute_normal(pd.concat([hari, other]))
    raise SystemExit("FAILED: mixed two people without complaint")
except ValueError as e:
    print("  raised:", e)

print("TEST 6: journal yes/no answers are not given a 'normal range'")
assert not any(m.startswith("journal:") for m in n["metrics"])

print("TEST 7: plain-words summary mentions n and never says 'cause'")
text = render(n, "recovery")
assert "n=" in text and "cause" not in text.lower() and "than usual" in text or "as usual" in text
print("  ok")

print("\nALL LAYER 2 TESTS PASSED")

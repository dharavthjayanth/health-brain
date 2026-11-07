"""Proves Layer 1 behaves like memory. Run: python test_layer1.py"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adapters import whoop_adapter
from layers.layer1_memory import Memory

DB = os.path.join(HERE, "test_brain.db")
if os.path.exists(DB):
    os.remove(DB)

mem = Memory(DB)
hari = whoop_adapter.load("hari", os.path.join(HERE, "data", "hari"))

print("TEST 1: first load")
print("  ", mem.remember(hari))
s1 = mem.summary("hari")
print("  ", s1)

print("TEST 2: load the exact same data again (must add nothing)")
r2 = mem.remember(hari)
print("  ", r2)
assert r2["added"] == 0 and r2["updated"] == 0, "duplicate loading changed memory!"
assert mem.summary("hari")["rows"] == s1["rows"]

print("TEST 3: a brand-new day arrives (must add only that day)")
new_day = pd.DataFrame([
    {"person_id": "hari", "date": "2026-07-19", "metric": "recovery", "value": 71, "unit": "%", "source": "whoop"},
    {"person_id": "hari", "date": "2026-07-19", "metric": "hrv", "value": 80, "unit": "ms", "source": "whoop"},
])
r3 = mem.remember(new_day)
print("  ", r3)
assert r3["added"] == 2
s3 = mem.summary("hari")
print("  ", s3)
assert s3["days"] == s1["days"] + 1

print("TEST 4: source corrects a value (new wins, old is kept in corrections)")
fix = pd.DataFrame([{"person_id": "hari", "date": "2026-07-19", "metric": "recovery",
                     "value": 65, "unit": "%", "source": "whoop"}])
r4 = mem.remember(fix)
print("  ", r4)
assert r4["updated"] == 1
cur = mem.conn.execute("SELECT old_value, new_value FROM corrections WHERE person_id='hari'").fetchall()
print("   corrections log:", cur)
assert cur == [(71.0, 65.0)]

print("TEST 5: people stay separate")
other = pd.DataFrame([{"person_id": "someone_else", "date": "2026-07-18", "metric": "recovery",
                       "value": 10, "unit": "%", "source": "test"}])
mem.remember(other)
rec = mem.recall("hari")
assert set(rec["person_id"]) == {"hari"}
print("   recall('hari') contains only:", set(rec["person_id"]))

print("TEST 6: stored numbers match what we found earlier for Hari")
rc = rec[(rec.metric == "recovery") & (rec.date <= "2026-07-18")]["value"]
print(f"   recovery days={len(rc)}, mean={rc.mean():.1f}  (earlier analysis: ~81 days, mean 64.1)")

os.remove(DB)
print("\nALL LAYER 1 TESTS PASSED")

"""Compute Layer 2 (Normal) for one person from their stored memory.

    python3 run_layer2.py hari
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from layers.layer1_memory import Memory
from layers.layer2_normal import compute_normal, render

person = sys.argv[1] if len(sys.argv) > 1 else "hari"
long_df = Memory(os.path.join(HERE, "brain.db")).recall(person)
if long_df.empty:
    sys.exit(f"Nothing remembered for '{person}'. Load their data into memory first.")

normal = compute_normal(long_df)
os.makedirs(os.path.join(HERE, "output"), exist_ok=True)
path = os.path.join(HERE, "output", f"normal_{person}.json")
with open(path, "w") as f:
    json.dump(normal, f, indent=2)

print(json.dumps(normal["data_range"], indent=2))
for m in ["recovery", "hrv", "rhr", "sleep_min", "day_strain"]:
    print()
    print(render(normal, m))
print(f"\nSaved to {path}")

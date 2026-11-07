# health-brain

A personal health brain: learns what is normal for ONE person from their own wearable data,
remembers their history, notices meaningful change, and explains it from that person's evidence only.

Read `PLAN.md` first (working agreement, access rules, design rules, layers), then the latest
entry in `LOG.md`.

## Layout
- `core_schema.py` the canonical schema every source is translated into
- `adapters/` one file per data source (only place allowed to know a source's column names)
- `layers/` one file per layer of the brain (layer1_memory.py is done)
- `test_layer1.py` tests for Layer 1

## Running the tests
Raw data is NOT in this repo (see `.gitignore`). Put a person's WHOOP export (four CSVs:
physiological_cycles, sleeps, workouts, journal_entries) in `data/<person>/`, then:

    python3 test_layer1.py

## Rules that matter
- Never commit raw health data, brain.db, or CSVs.
- No ML, no causal language, never mix people, say "not enough data yet" when true.

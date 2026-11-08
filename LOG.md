# LOG

## 2026-11-08 (daytime, agent working alone; for review this evening)
- Built Layer 2 (Normal): layers/layer2_normal.py, run_layer2.py, test_layer2.py. 7 tests pass,
  Layer 1 tests still pass. Numbers match the earlier analysis (recovery avg 64.1 over 81 days,
  HRV 77.5, sleep 388 min).
- Rules enforced in code: under 5 days of a metric or under 8 days in a comparison group gives
  "not enough data yet" with no numbers; refuses to mix two people; missing days are never filled in.
- Things in Hari's data worth discussing this evening (observations only, not conclusions):
  * Last 14 days (only 8 of them have a reading): recovery 50.0 vs 65.7 before, HRV 69.2 vs 78.5,
    sleep 346 vs 393 min, resting HR 59.6 vs 57.1. Everything moved the "worse" way together.
    The data ends 2026-07-18, so this is old news, but it is the kind of thing Layer 4 should flag.
  * Weekend sleep is much shorter: 328 vs 411 min on weekdays (n=22 vs 59).
  * Counterintuitive again: HRV is a little LOWER on longer-sleep days (75.5 vs 79.7). Same flavour
    as the earlier "recovery higher after lower sleep efficiency" result. Do not smooth this away;
    look at it properly in Layer 3.
- Not done: Syam's data (lost in the reset, needs re-uploading). No daily scheduled run yet.
- Pushing to GitHub works (Claude app installed on the repo).

## 2026-11-07 (evening session, together)
- Built Layer 1 (Memory) for Hari: 1,812 observations, 82 days, 23 metrics in brain.db.
- 6 tests pass: first load, repeat load adds nothing, new day appends only that day, a corrected
  value keeps the old one in a corrections table, people stay separate, numbers match earlier
  analysis (81 recovery days, mean 64.1).
- The sandbox was reset earlier this day and the older prototype code was lost. Layer 1 was
  rebuilt from scratch. Syam's files were lost too and need re-uploading.
- Decided: daily agent run plus evening review together. Ask-first access model.
- Next: Layer 2 (Normal).

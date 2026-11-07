# Personal Health Brain: PLAN

North star: learn what is normal for ONE person from their own data, remember their history,
notice meaningful change, and explain it using only that person's evidence.

## Working agreement (daily rhythm)
- Daytime run (agent, unattended): read this file and the last LOG entry, do ONE small step of the
  current layer, run the tests, write a handoff note in LOG.md.
- Evening (Jayanth + Claude, together after 6:30 PM IST): review the note, understand what was
  built and why, decide the next step, update this plan.
- The agent never moves to the next layer without Jayanth's sign-off.
- A step counts as done only if the tests pass. Unfinished work is logged as unfinished.

## Access rules (ask-first)
- Allowed without asking: read the project, search the web, run code, write inside the project folder.
- Must ask first (write the question in the handoff note and wait): any new connector or account,
  sending messages, deleting anything, installing anything outside the project, touching work tools
  (ClickUp, BigQuery, Chrome), uploading raw health data anywhere.
- Raw health data (CSV exports, brain.db) never goes into shared storage. Code and notes only.

## Design rules (do not drift)
1. Device-independent: only an adapter may know a source's column names.
2. Canonical schema: person_id | date | metric | value | unit | source.
3. Statistical honesty: minimum sample sizes, stricter bar for behavioral (journal) patterns,
   top few only, always labeled "needs replication". Say "not enough data yet" when true.
4. Association language only ("historically associated with"), never causal.
5. No machine learning or neural networks until there are far more people (thousands), not months.
6. Everything is relative to the person's OWN history. Never population norms. Never mix people.
7. Every pattern keeps a history of snapshots over time (the actual "memory").
8. The language layer only describes computed evidence. It never computes or invents numbers.

## Layers
1. Memory: DONE. SQLite store, no duplicates, corrections logged, people kept apart.
2. Normal: NEXT. Typical range per metric, weekday vs weekend, high vs low load, trend over time.
3. Patterns: what tends to happen together, with sample sizes and confidence labels.
4. Change: today and this week versus own normal; which other metrics moved with it.
5. Evidence graph: patterns as nodes and edges, each with a history of confidence over time.
6. Voice: answer questions using only what layers 1 to 5 hold.

## Known facts about Hari's data (checked)
- 82 days (2026-03-25 to 2026-07-18), 23 stored metrics, about 30% of calendar days missing.
- Body and sleep metrics are solid. Journal has almost no variance (only "ate food close to bedtime"
  is usable). Most workouts are unlabeled, so use strain and duration, not workout type.
- Earlier prototype finding worth re-checking in Layer 3: recovery looked HIGHER after lower sleep
  efficiency, which is counterintuitive. Do not smooth it away.

## Open questions for Jayanth
- Permanent home for the code (private GitHub repo vs folder on his computer).
- Where Hari's raw data should live so the daytime agent can reach it without it being shared.
- Syam's data needs re-uploading (the workspace reset lost it).

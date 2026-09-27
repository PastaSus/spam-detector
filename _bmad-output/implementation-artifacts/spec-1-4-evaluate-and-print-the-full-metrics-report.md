---
title: 'Story 1.4: Evaluate and Print the Full Metrics Report'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The user needs accuracy, precision/recall/F1, and a confusion matrix printed after training — before trusting the model interactively.

**Approach:** Compute all three via sklearn and render a fixed 2×2 grid; show the demo-data warning banner on fallback runs (AD-B6); `--no-loop` prints and exits 0 without touching stdin.

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build; spec reconstructed from `epics.md` + code.
- `evaluate.py`: `EvaluationReport` (JSON-native fields) / `evaluate` / `format_report`; `cli.py` train path prints banner + report.
- Covered by `test_evaluation_metrics` and the CLI fallback-banner test.

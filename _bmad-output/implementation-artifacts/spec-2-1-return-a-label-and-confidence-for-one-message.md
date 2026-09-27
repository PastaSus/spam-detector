---
title: 'Story 2.1: Return a Label and Confidence for One Message'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Each prediction must carry a confidence percentage so borderline messages are distinguishable from obvious ones.

**Approach:** `predict_proba()` mapped through `pipeline.classes_` (never positional order — AD-B3), returned as `(label_str, confidence_pct)` under the `1 = spam` / `0 = ham` contract (AD-B1, FR-B5).

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build; spec reconstructed from `epics.md` + code.
- `model.py`: `predict_label` / `predict_with_confidence` / `display_label`.
- Covered by contract, prize-spam, meeting-ham, and unicode agreement tests.

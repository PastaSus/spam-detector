---
title: 'Story 1.2: Load Datasets From File or Built-in Fallback'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The classifier must find data with zero configuration and explain itself when the real dataset is missing.

**Approach:** Resolution order `--data` > `data/sms_spam_collection.csv` > 23-row built-in fallback with all seven lab families; warn on fallback (NFR-B2); tolerate headers, case-varied labels, and unmappable rows (NFR-B3, AD-B1, AD-B2).

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build; spec reconstructed from `epics.md` + code.
- `dataset.py`: `resolve_dataset_path` / `load_dataset` / `normalize_label`; header and unmappable rows dropped with a warning count.
- Deliberate AC refinement (documented): an *explicit* missing `--data` path raises `FileNotFoundError` (fail loudly for user-specified input) instead of falling back; only default resolution falls back with a warning (`test_explicit_missing_file_raises`, `test_missing_file_falls_back_to_builtin`).
- Covered by `TestDataset` (fallback shape, label variants, CSV round-trip, header drop, fallback warning via CLI test).

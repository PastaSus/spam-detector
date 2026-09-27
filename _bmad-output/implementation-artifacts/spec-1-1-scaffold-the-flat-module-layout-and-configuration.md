---
title: 'Story 1.1: Scaffold the Flat Module Layout and Configuration'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Every later story needs one source of truth for layout and tunable constants instead of hard-coded values scattered across modules.

**Approach:** Scaffold the flat root layout (`main.py`, `cli.py`, `config.py`, `dataset.py`, `model.py`, `evaluate.py`, `conftest.py`, `tests/`) with all constants centralised in `config.py`, folders kebab-case and modules snake_case (AD-1, AD-2).

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build (first commit); spec reconstructed from `epics.md` + code.
- `config.py`: `RANDOM_STATE = 42`, `TEST_SIZE = 0.2`, `TFIDF_PARAMS`, `CLASSIFIERS`, `DEFAULT_CLASSIFIER`, path constants, `SPAM = 1` / `HAM = 0`; no other module re-declares them (verified by inspection).
- `conftest.py` puts the project root on `sys.path` so flat imports resolve under pytest.

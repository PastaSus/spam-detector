---
title: 'Story 1.3: Train the Reference Pipeline With a Deterministic Split'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Results must reproduce the lab reference sheet exactly and repeat identically every run.

**Approach:** Lab-exact `Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])` with `lr` alternative; `train_test_split(..., stratify=y, random_state=42)`; actionable errors on unstratifiable data (AD-B4); one-way module graph, no network (AD-4, NFR-B4).

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build; spec reconstructed from `epics.md` + code.
- `model.py`: `build_pipeline` / `train`; `dataset.py`: `split_data` with guards (<4 rows, <2 classes, <2 rows/class, test-split-smaller-than-classes, `test_size` validation).
- Covered by structure/alternative/determinism/guard tests; acyclic graph proven by `test_no_circular_imports`.

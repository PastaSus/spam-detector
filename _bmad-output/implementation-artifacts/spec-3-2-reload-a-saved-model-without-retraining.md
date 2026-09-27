---
title: 'Story 3.2: Reload a Saved Model Without Retraining'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `--load-model` skips training but prints only "evaluation skipped" — the stored metrics from story 3.1 are never shown, and the load path has no CLI-level tests for its success, missing-file, or prediction-identity behaviour.

**Approach:** Add a small sidecar reader in the model layer, have the CLI's load branch print the stored report through the same renderer as the train path when a sidecar exists, and cover the three acceptance criteria with CLI-level tests. Missing-file handling already exits non-zero without a traceback; it only needs a test to lock it in.

</frozen-after-approval>

## Implementation Notes

- `model.py`: added `load_metrics()` — reads the `<stem>-metrics.json` sidecar, returns `{}` when absent so the CLI treats it as "not available". Malformed JSON surfaces as `ValueError` (a `JSONDecodeError`), which `main()` already converts to exit 1.
- `cli.py`: load branch prints stored metrics via the same `format_report(EvaluationReport(**stored))` renderer as the train path when a sidecar exists; otherwise keeps the "(evaluation skipped)" line. Missing-file path untouched (already exit 1, no traceback).
- `tests/test_pipeline.py`: 3 new CLI-level tests (stored metrics printed, no-sidecar fallback, missing path exits 1). Prediction identity across save/load already locked by 3.1's round-trip test. Suite: 34 passed; `compileall` clean.
- Review follow-ups: corrupt-sidecar shape now fails clean (exit 1, no traceback) with a test; added load-ignores-dataset lock, missing-path message assertion, and `load_metrics` empty-dict unit test. Suite: 37 passed; `compileall` clean.

## Review Triage Log

- Unvalidated sidecar shape → raw traceback on drifted JSON → patched: metrics rendering wrapped, shape errors re-raised as `ValueError` (exit 1, clean message); covered by corrupt-sidecar test.
- `load_metrics` outside try / no corrupt-sidecar test → same root cause as above, patched together.
- No CLI-level prediction-identity test → rejected as low: the prediction code path is identical however the pipeline was obtained, and 3.1's round-trip test already locks identity.
- No lock that load skips training/dataset resolution → patched: load run with an absent `--data` path still exits 0.
- Missing-path test asserts only exit code → patched: now also asserts the "Could not load model" message via `caplog`.
- Silently ignored flags with `--load-model` → deferred: already recorded in `deferred-work.md` during 3.1; no new entry.
- No provenance in printed metrics → deferred: already recorded in `deferred-work.md`; no new entry.
- `load_metrics` `{}`-when-absent untested → patched: direct unit test added.
---
title: 'Story 3.1: Persist the Trained Model and Its Metrics'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-3-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** `--save-model` serialises the pipeline to `models/spam-model.joblib` but drops the run's metrics, so story 3.1's acceptance criteria (model plus its metrics stored, directory auto-created) are only half met.

**Approach:** Extend the save path to also write the evaluation report as a JSON sidecar next to the model file (`<stem>-metrics.json` in the same directory, directory created if absent), pass the report from the CLI's train path, and cover save behaviour with round-trip tests. Loading and printing the stored metrics stays in story 3.2.

</frozen-after-approval>

## Implementation Notes

- `model.py`: added `metrics_path_for()` (`<stem>-metrics.json` beside the model file); `save_model()` takes optional `metrics` mapping and writes it as indented JSON sidecar. Kept `load_model()` untouched and the `Pipeline` return contract intact for story 3.2. `EvaluationReport` fields were already JSON-native, so the CLI passes `dataclasses.asdict(report)` with no conversion layer.
- `cli.py`: train path passes `asdict(report)` to `save_model()`; save confirmation now names the sidecar.
- `tests/test_pipeline.py`: new `TestPersistence` (4 tests: sidecar naming, save+sidecar content equality, no-sidecar without metrics, reload prediction identity). Suite: 30 passed; `compileall` clean; CLI smoke-tested with `--save-model` to a temp path (sidecar verified, files removed).
- Review follow-ups: serialize-first ordering (fail before any file is written) plus trailing newline in the sidecar; added CLI passthrough test (`test_cli_save_model_passes_report`); deferred load+save combo warning and sidecar provenance to `deferred-work.md`. Suite: 31 passed; `compileall` clean.

## Review Triage Log

- Orphan model on bad metrics mapping → low, patched: payload is serialised before any file is written, so a bad mapping fails with nothing on disk.
- Stale sidecar when re-saving without metrics → rejected as low: unreachable via the CLI (always passes metrics); auto-deleting user files would add riskier semantics than the wart it fixes.
- `--save-model` silently ignored with `--load-model` → deferred: pre-existing behaviour in the load branch, which story 3.2 owns; entry added to `deferred-work.md`.
- Sidecar lacks run provenance → deferred: beyond story 3.1 AC, enhancement; entry added to `deferred-work.md`.
- `metrics_path_for` edge cases (str input, extensionless, multi-suffix) → false: `Path()` accepts strings and `stem` handles all three deterministically.
- No CLI-level passthrough test → patched: added `test_cli_save_model_passes_report` driving `run()` with a `Namespace`.
- Uncaught `TypeError` from `json.dumps` in `main` → rejected: unreachable via the CLI (report fields are coerced to natives in `evaluate()`); direct-API misuse now fails loudly before writing anything.
- Missing trailing newline in sidecar → low, patched: payload ends with `"\n"`.

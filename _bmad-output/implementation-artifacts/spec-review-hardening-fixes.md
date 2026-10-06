---
title: 'Pre-demo review hardening batch'
type: 'bugfix'
created: '2026-10-06'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The pre-demo `bmad-review` pass produced 22 findings; four are demo-risky or close verification gaps: train-only flags are silently ignored with `--load-model`, Ctrl+C during train/evaluate escapes as a traceback, and the `--classifier lr` and TSV code paths have no end-to-end test.

**Approach:** Harden `cli.py` with ignored-flag warnings and a clean KeyboardInterrupt exit, and add the two missing CLI/dataset tests; verify with the full suite plus `compileall`.

</frozen-after-approval>

## Implementation Notes

VCS note: tree carries one dirty file, root `PROMPTS_LOG.md` (append-only QA-006 row), disjoint from this scope — fix work goes on a new `fix/` branch; prompt rows get their own `chore(prompts)` commit afterwards.
Decisions: warnings via `logger.warning` (matches existing `--save-model` pattern); KeyboardInterrupt exits 130; existing `test_cli_load_model_ignores_missing_dataset` stays green because the new behavior warns, never errors.
Review patches (blind-hunter follow-ups, same scope): `main()` docstring now lists exit 130; `--load-model` help notes train-only flags are ignored; warning test parametrized per-flag with negative assertions; TSV test parametrized over `.tsv`/`.tab`/`.TSV`. Branch: `fix/review-hardening-gaps`. Suite: 92 passed, `compileall` clean.

## Review Triage Log

- Docstring omits exit 130 — low, patched (docstring updated).
- `--help` does not document ignored flags — low, patched (help text updated).
- Explicit default values produce no warning — low, rejected (needs sentinel defaults; corner-of-corner, harm negligible).
- `Namespace` missing attributes → uncaught `AttributeError` — false (argparse always sets all attributes; unreachable).
- `print` to stdout with unconditional `\n` — false (mirrors `_interactive_loop` Ctrl+C convention).
- Warning test lacks single-flag isolation — low, patched (parametrized with negative assertions).
- KeyboardInterrupt test uses a stub — low, rejected (real-signal test would be flaky; contract test suffices).
- TSV test lacks `.tab`/uppercase coverage — low, patched (parametrized); row-count part — false (exact `[0, 0, 1, 1]` match already pins length).

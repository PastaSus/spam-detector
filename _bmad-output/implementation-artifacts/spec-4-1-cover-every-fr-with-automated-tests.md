---
title: 'Story 4.1: Cover Every FR With Automated Tests'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** FR-B1 through FR-B5 and FR-B7 each trace to passing tests, but FR-B6 (interactive loop: classify, `quit`/`exit`/`:q`, blank re-prompt, clean EOF exit) has zero coverage, so "every FR traceable to at least one test" fails.

**Approach:** Add deterministic offline tests driving the interactive loop with scripted stdin (classify output format, exit commands, blank re-prompt, EOF exit with code 0 and no traceback), plus an FR→test traceability table in the test module docstring. No source changes expected — the loop already handles all four behaviours.

</frozen-after-approval>

## Implementation Notes

- `tests/test_pipeline.py` only: new `TestInteractiveLoop` (5 tests, 8 cases — classify+quit, all four exit commands incl. case-insensitivity, blank re-prompt, EOF exit, `SPAM/HAM (NN.N% confidence)` output format) driving `_interactive_loop` with scripted `builtins.input`; plus an FR→test traceability table in the module docstring. No source changes — the loop already handled every behaviour. Suite: 45 passed; `compileall` clean.
- Review follow-ups: two-message session test with exact confidence count, padded/embedded exit-word cases, Ctrl+C test, blank test with input-call proof incl. tab, tightened HAM format regex. Suite: 48 passed; `compileall` clean.

## Review Triage Log

- No Ctrl+C test → patched: `test_loop_keyboard_interrupt_exits_cleanly` added.
- Exit tests never assert no label printed → patched: `confidence not in out` asserted; also defeats synthetic-EOF masking for those tests.
- Thin exit-variant coverage → patched: added padded `"  quit  "` and a "message containing an exit word still classifies" test locking exact-match semantics.
- Blank test proves no re-prompt and misses tab → patched: input calls recorded and asserted, `\t` added.
- Synthetic EOF could mask a loop ignoring quit → patched: session test asserts exactly 2 confidence lines, so a classified `quit` would fail it.
- No multi-message session / padded input → patched: session test classifies two messages incl. a whitespace-padded one; intro/prompt text assertions declined as cosmetic.
- Lax format regex → patched: tightened to two-space prefix with explicit `HAM` for the ham fixture input.
- Per-test retraining / no explicit random_state / no `run()` wiring test → rejected: 23-row retrain costs milliseconds, determinism comes from the config default all tests share, and `run()` calls the same loop function directly.
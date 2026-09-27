---
title: 'Story 2.2: Run the Interactive Loop With Clean Exits'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: [] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The user needs a prompt for ad-hoc classification that always exits cleanly — no tracebacks on quit paths.

**Approach:** `sms>` loop printing `SPAM/HAM (NN.N% confidence)`; blank input re-prompts; `quit`/`exit`/`:q`/EOF/Ctrl+C print goodbye and exit 0 (FR-B6).

</frozen-after-approval>

## Implementation Notes

- Backfilled 2026-09-27: implemented pre-build; spec reconstructed from `epics.md` + code.
- `cli.py`: `_interactive_loop`; exit code 0 flows through `run`/`main`.
- Covered by `TestInteractiveLoop` (session, exit commands, blanks, EOF, Ctrl+C, format) plus CLI-level EOF and exact-spec-strings tests.

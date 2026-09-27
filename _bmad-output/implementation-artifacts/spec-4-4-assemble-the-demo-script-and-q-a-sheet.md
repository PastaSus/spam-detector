---
title: 'Story 4.4: Assemble the Demo Script and Q&A Sheet'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Phases 5–6 need a rehearsed demo script and a professor Q&A sheet, and neither exists — the CLI works but there is no written walkthrough with expected outputs and no cited answers to anticipated questions.

**Approach:** Add `docs/demo-script.md` (dataset resolution, training, metrics, interactive classification, save/load — every step with the real expected output captured from the CLI) and `docs/qa-defense-sheet.md` (one row per anticipated question, each citing the FR/AD or test that answers it). Docs only, no code changes.

</frozen-after-approval>

## Implementation Notes

- `docs/demo-script.md`: 6 rehearsed steps (resolution, training/metrics, explicit file, interactive loop, save/load, gates) with outputs captured from live CLI runs; save/load step re-verified verbatim (`models/` residue removed afterwards).
- `docs/qa-defense-sheet.md`: 16 questions, each citing FR/AD/NFR or named tests. Docs only, no code changes.
- Review follow-ups: verbatim banner borders + log line, dropped-row warning, `--no-loop` on the load demo (it would hang in the loop), Windows separator note, model precondition for confidence numbers, `models/` cleanup, 7-test list fix, exact test-name citations, `evaluate → model` graph edge, 2 new rows (label contract, exit codes/flags). Suite still 71 green.

## Review Triage Log

- Banner borders/log line omitted → patched: verbatim block with machine-specific path elided.
- Dropped-row warning omitted → patched: warning line plus say-line.
- Load demo missing `--no-loop` → patched: would have hung in `sms>` loop.
- Mixed separators → patched: one Windows-rendering note at top; echo line corrected to match typed separators.
- Confidence numbers lack precondition → patched: fallback-model note.
- No `models/` cleanup → patched: cleanup line added.
- "7 meta-tests" lists 6 → patched: module/class docstrings listed distinctly.
- Vague test citations → patched: exact test names throughout.
- AD-5 vs AD-B5 "inconsistency" → false: verified in `system-architecture.md` — AD-5 is the prompt log, AD-B5 is persistence; both cited correctly.
- Graph omits `evaluate → model` → patched.
- Missing label contract / exit codes / flags / TSV → patched: 2 new rows (17–18).
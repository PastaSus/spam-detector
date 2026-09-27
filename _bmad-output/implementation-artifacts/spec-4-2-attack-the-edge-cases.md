---
title: 'Story 4.2: Attack the Edge Cases'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Three of story 4.2's four adversarial cases lack proof: unicode input has no test at all, EOF-to-exit-code-0 is only shown at loop level (never through `main()`), and two of `split_data`'s three actionable-message guards (tiny frame, thin class) are untested. Missing-file fallback and single-class rejection are already locked.

**Approach:** Add a `TestEdgeCases` class with deterministic offline tests — unicode classification contract (emoji, CJK, accents), CLI-level EOF stdin exiting 0, CLI fallback run warning plus exit 0, and the two untested split guards. No source changes expected — every behaviour already exists.

</frozen-after-approval>

## Implementation Notes

- `tests/test_pipeline.py` only: new `TestEdgeCases` (7 cases — unicode contract over emoji/CJK/accents, tiny-frame and thin-class split guards, CLI-level EOF stdin exiting 0, CLI fallback run warning plus exit 0). No source changes — every behaviour already existed. Suite: 55 passed; `compileall` clean.
- Review follow-ups: predict-agreement assertion; empty/whitespace/RTL/zero-width/long unicode cases; parametrized tiny-frame sizes plus minimal-balanced positive boundary; no-traceback and banner-content assertions; new `split_data` guard rejecting test splits smaller than the class count (the one case needing a source change) with tests. Malformed-file robustness deferred. Suite: 64 passed; `compileall` clean.

## Review Triage Log

- Unicode predict/label agreement unasserted → patched: consistency asserted via the `SPAM` contract.
- Thin unicode variety → patched: added empty, whitespace-only, RTL/zero-width, and 5000-char cases; loop/main print-path coverage declined as cosmetic (same in-process print path).
- Tiny-frame only 3-row, no positive boundary → patched: parametrized 0–3 rows plus a minimal-balanced 4-row split-acceptance test (also covers the thin-class positive boundary).
- EOF test asserts no stderr check → patched: asserts no "Traceback" on stderr (exact-empty impossible — the fallback warning logs there by design).
- Fallback test asserts only DEMO → patched: also asserts row-count line, real-data guidance, and printed metrics.
- Untestable stratify (test rows < classes) surfaces raw sklearn error → patched in source: `split_data` raises an actionable `ValueError` first, with reject/accept tests.
- Empty/overlong inputs and malformed files (empty, single-column, bad labels, BOM) → split: empty/whitespace/long inputs patched into the unicode test; malformed-file hardening deferred to `deferred-work.md` (beyond story ACs).
- Fixture duplication / local imports / single-use `io` → rejected: all three match the file's existing per-class-fixture and local-import conventions.
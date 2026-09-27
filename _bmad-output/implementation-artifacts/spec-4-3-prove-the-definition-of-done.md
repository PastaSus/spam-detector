---
title: 'Story 4.3: Prove the Definition of Done'
type: 'feature' # feature | bugfix | refactor | chore
created: '2026-09-27'
status: 'done' # draft | ready-for-dev | in-progress | in-review | done
route: 'oneshot' # oneshot | dispatch — set by step-02's route gate after design
review_loop_iteration: 0 # incremented by step-04 before each review loopback
context: ['{project-root}/_bmad-output/implementation-artifacts/epic-4-context.md'] # optional: `{project-root}/`-prefixed paths to project-wide standards/docs the implementation agent should load. Keep short — only what isn't already distilled into the spec body.
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The static half of the DoD ("no circular imports, typed public APIs, docstrings, no print debugging", plus the append-only prompt log) currently rests on eyeballing — and an audit found real violations: four public functions without docstrings, three without full annotations, and no mechanical check on `PROMPTS_LOG.md` ID hygiene.

**Approach:** Fix the violations (docstrings, annotations) and encode every static gate as an AST- and parse-based meta-test module so `pytest` itself proves the DoD. CLI `print()` calls stay — they are user-facing output, not debugging.

</frozen-after-approval>

## Implementation Notes

- Source fixes from the audit: docstrings for `cli.build_parser/run/main` and `model.display_label`/`evaluate.accuracy_pct`; annotations for `dataset.split_data` return, `model.train` inputs (`pd.Series`), `evaluate.evaluate` inputs (`Pipeline`, `pd.Series`).
- New `tests/test_definition_of_done.py`: 5 meta-tests (first-party import DAG cycle check, public docstrings, public annotations incl. class methods, no `print()` outside `cli.py`, prompt-log ID format/uniqueness/per-phase ordering). Suite: 69 passed; `compileall` clean.
- Review follow-ups: dynamic module discovery; unified private rule plus `*args`/`**kwargs`; module/class docstring gate; `get_type_hints` resolvability; banned-output set (`pprint`/`breakpoint`/`sys.stdout.write`); prompt-log date/cell/status strictness; `py_compile` gate over the exact AC file list; typed/documented the three private helpers. Suite: 71 passed; `compileall` clean.

## Review Triage Log

- Hardcoded module list → patched: root `*.py` discovery.
- Static-only cycle check → rejected as low: `ast.walk` already covers nested/conditional static imports and the repo has no dynamic imports.
- `*args`/`**kwargs` skipped, dunder rule inconsistent → patched: unified to a single leading-underscore rule, vararg/kwarg included.
- Classes/module docstrings unchecked → patched: new gate; all pass.
- Annotations unchecked for resolvability → patched: `get_type_hints` must succeed per function; TYPE_CHECKING objection rejected (runtime imports are cheap, deps are hard, no cycle risk).
- Output gate misses `pprint`/`breakpoint`/`sys.stdout.write`, cli.py blanket allow → patched the callee set (none exist); cli.py allowlist kept as the recorded UI-vs-debug decision.
- Prompt-log test thin → patched: date shape, 6 cells, persona/prompt non-empty, status allowlist.
- Missing INIT-001..003 rows → no code action: documented backfill debt owned by the Tech Lead; flagged for sign-off.
- No DEV/QA rows for recent stories → rejected as false: every user prompt was logged (the INIT kickoffs); no prompt went unlogged. Whether per-story DEV rows are wanted is a Tech Lead process call.
- No compileall gate → patched: `py_compile` over the exact AC file list.
- Private helpers excluded → patched at the source: typed `pipeline`, documented both dataset helpers.
- Tuple-order fragility / narrow Series types → rejected as low: order is asserted positionally by the split test, inputs are Series at every call site.
- Terse docstrings → rejected: DoD requires presence, not numpydoc completeness.
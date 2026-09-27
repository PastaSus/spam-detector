# Epic 4 Context: Adversarial Hardening and Defense Readiness

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Let the Tech Lead defend the deliverable with evidence: full test traceability, adversarial edge-case coverage, machine-checkable quality gates, logged prompts, and a rehearsed demo with Q&A for final sign-off. Note: only the epics file was available — no separate PRD, architecture, or design artifacts were found — so this context is distilled from the epic breakdown alone.

## Stories

- Story 4.1: Cover Every FR With Automated Tests
- Story 4.2: Attack the Edge Cases
- Story 4.3: Prove the Definition of Done
- Story 4.4: Assemble the Demo Script and Q&A Sheet

## Requirements & Constraints

- Test suite must run offline, deterministically, and pass fully; every functional requirement must be traceable to at least one passing test.
- Missing dataset files must fall back with a warning rather than crashing.
- Single-class or otherwise unstratifiable data must fail fast with a clear actionable message.
- Closed stdin must exit cleanly with a goodbye and zero status, never a traceback.
- Non-ASCII message text must classify without encoding errors.
- Definition of done requires clean byte-compilation, a green suite, no circular imports, type hints on public APIs, docstrings on public functions, no leftover debug printing, and an append-only log of every user-to-AI prompt.
- Demo script must walk dataset resolution, training, metrics, interactive classification, and save/load with expected outputs; Q&A answers must cite the behavior or test that backs them.
- Phase board may only be updated once artifacts exist, prompts are logged, and the Tech Lead signs off.
- Must work offline with no network access.

## Technical Decisions

- Keep all automated verification deterministic with a fixed random seed and no network use.
- Handle failure modes with user-facing messages and defined exit codes rather than raw exceptions.
- Store the prompt log as append-only rows at the project root; verification checks its presence and format.
- Bundle demo evidence from the existing training, evaluation, interactive, and persistence flows rather than building new runtime paths.

## Cross-Story Dependencies

- Definition-of-done checks build on the automated and adversarial tests; demo and Q&A build on the finished flows from earlier epics.
- Final sign-off and phase-board update are gated on all test, logging, demo, and Q&A artifacts being complete.

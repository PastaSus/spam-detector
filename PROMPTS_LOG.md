# PROMPTS_LOG — spam-detector

Append-only prompt log (Professor requirement · architecture AD-5 · `docs/bmad-plan.md` §4).

**Protocol**

- One entry per user → AI prompt, in order.
- ID format: `<PHASE>-<NNN>` — prefixes `INIT`, `PM`, `ARCH`, `DEV`, `QA`.
- Log prompts **verbatim**, with date, persona, artifacts, and status.
- Re-prompts and corrections are **new** entries; never overwrite an existing row.
- Owned by the Tech Lead; a phase is not Done until its prompts are logged.

> Backfill note: `INIT-001`, `INIT-002`, and `INIT-003` are cited as complete in
> `docs/bmad-plan.md` but predate this file — Tech Lead to backfill those rows.

| ID | Date | Persona | Prompt (verbatim) | Artifacts | Status |
|---|---|---|---|---|---|
| INIT-004 | 2026-09-27 | Tech Lead | bmad-help what bmad workflow should we get started on? crawl the whole codebase and also put folders _bmad,.agents.opencode to gitignore since we dont have one and what else do we need to put in gitignore? | `.gitignore` (root) | Done |
| INIT-005 | 2026-09-27 | Tech Lead | yeah do PC first | `AGENTS.md` (root), `PROMPTS_LOG.md` (root), `.venv` (uv, CPython 3.12) | Done |
| PM-001 | 2026-09-27 | PM Agent | yes and also do SP immediately after that dont wait for my approval we wanna go through this fast. | `_bmad-output/planning-artifacts/epics.md` (4 epics / 12 stories), `_bmad-output/implementation-artifacts/sprint-status.yaml` | Done |
| INIT-006 | 2026-09-27 | Tech Lead | bmad-help crawl the whole codebase for our progress in bmad-method we should be at implementation now and also specifically _bmad-output folder and agents.md file actually | status orientation only (no artifacts changed); progress read from `docs/bmad-plan.md`, `_bmad-output/` | Done |
| INIT-007 | 2026-09-27 | Tech Lead | what do you recommend we do first? BD or do CR , SS(pretty sure theres no missing story file but go ahead if you recommend it) | recommendation only (no artifacts changed); verified FR coverage in `tests/test_pipeline.py`, FR-B7 code in `model.py`/`cli.py` | Done |
| INIT-008 | 2026-09-27 | Tech Lead | this is the fresh context. lets get started then branches and all | branch `feat/3-1-persist-the-trained-model-and-its-metrics`; story 3.1 per `_bmad-output/planning-artifacts/epics.md` | In progress |
| INIT-009 | 2026-09-27 | Tech Lead | merge done next story i guess | PR #1 merged to `main` (`4fe2e48`); local story branch deleted; story 3.2 next | Done |
| INIT-010 | 2026-09-27 | Tech Lead | pr done. next | PRs #2/#3 merged to `main`; local 3.2 branch deleted; story 4.1 next | Done |
| INIT-011 | 2026-09-27 | Tech Lead | pr doone next | PR #4 merged to `main`; local 4.1 branch deleted; story 4.2 next | Done |
| INIT-012 | 2026-09-27 | Tech Lead | next | PR #5 merged to `main`; local 4.2 branch deleted; story 4.3 next | Done |
| INIT-013 | 2026-09-27 | Tech Lead | pr done next. | PR #6 merged to `main`; local 4.3 branch deleted; story 4.4 next | Done |
| INIT-014 | 2026-09-27 | Tech Lead | time for review we also need to clean the branches right? | code review run; merged remote story branches deleted | In progress |
| INIT-015 | 2026-09-27 | Tech Lead | 1 | apply all 6 code-review patch entries on a fix/ branch with atomic commits | In progress |
| INIT-016 | 2026-09-27 | Tech Lead | what about epic 1,2 code-review? | Epic 1-2 code was inside the reviewed full-build diff; offered targeted pass vs accept | Done |
| INIT-017 | 2026-09-27 | Tech Lead | aight option 1 then. | accepted full-build coverage; all 12 stories + 4 epics marked done | Done |
| INIT-018 | 2026-09-27 | Tech Lead | what do you recommend | recommended AGENTS.md block, flag-combo fix, INIT backfill by user, skip retrospective | Done |
| INIT-019 | 2026-09-27 | Tech Lead | alright go ahead | approved AGENTS.md splice + flag-combo fix (queued behind story backfill) | Done |
| INIT-020 | 2026-09-27 | Tech Lead | we dont have epic 1 and epic 2 stories in _bmad-output/implementation-artifacts folder thats weird make sure to generate them | backfill story spec files 1-1..2-2 as done from epics.md + code | Done |
| INIT-021 | 2026-09-27 | Tech Lead | do that then? | AGENTS.md git-rules splice + load/save combo fix | In progress |
| QA-001 | 2026-10-06 | Tech Lead | bmad-help crawl the codebase and teach me how to use this spam detector program that imm video demo to my prof and also he will ask questions about source code. | orientation only (no artifacts changed); verified live: 84 passed, fallback metrics 0.60 | Done |
| QA-002 | 2026-10-06 | Tech Lead | yes go ahead | `docs/demo-script.md` + `docs/qa-defense-sheet.md` test-count fixes (71→84) on branch `docs/fix-stale-test-counts`; bmad-review report (adversarial/edge/verification lenses) | Done |
| QA-003 | 2026-10-06 | Tech Lead | go ahead and make the branch and atomically and aconventionally commit changes | branch `docs/fix-stale-test-counts`; `0126570` docs(demo) + `e6a023d` chore(prompts) | Done |
| QA-004 | 2026-10-06 | Tech Lead | list of things left todo? | status list only (no artifacts changed) | Done |
| QA-005 | 2026-10-06 | Tech Lead | done merging to mmain | PR #11 merged; branch cleanup + QA-003/QA-004 commit queued | Done |

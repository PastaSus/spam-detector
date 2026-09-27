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

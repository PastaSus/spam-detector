<!-- bmad:context -->
<!-- Verified 2026-10-06 against 6b14e75. Managed by bmad-project-context; edits inside this block are replaced on refresh. Keep anything you want preserved outside the markers. -->

## spam-detector

SMS spam text classifier for the university semifinals case study (Project B). Flat Python + scikit-learn CLI — not a package. BMAD-managed: requirements, architecture, and the phase board live in `docs/`; generated artifacts land in `_bmad-output/`.

## Policy

- Work on a branch per sprint story off `main` — `feat/<story-key>` (e.g. `feat/3-1-persist-the-trained-model-and-its-metrics`), or `fix/`/`chore/`/`docs/`; merge back to `main`, then delete the branch — never commit story work straight onto `main`.
- Commit atomically, one concern per commit, as Conventional Commits `type(scope): subject` (`feat(dataset): …`, `fix(cli): …`, `test`, `docs`, `chore`); never bundle unrelated changes — `PROMPTS_LOG.md` entries go in their own commit, not with code.
- Append every user→AI prompt to root `PROMPTS_LOG.md` under a `<PHASE>-<NNN>` ID (prefixes `INIT`/`PM`/`ARCH`/`DEV`/`QA`) — append-only, never overwrite; re-prompts are new entries.
- Never hand-edit `_bmad/` or `.agents/` — installer-managed; re-run the BMAD installer instead.
- Never fabricate or commit `data/sms_spam_collection.csv` (user-supplied, gitignored). `models/` is gitignored too — regenerate weights, don't commit them.
- PRD and architecture in `docs/` are signed-off Baseline v1.0 — raise changes through `bmad-prd` / `bmad-architecture`, don't edit them directly.
- Never mark a phase Done in `README.md` or `docs/bmad-plan.md`; only the Tech Lead signs off.

## Where things are

- Entry point: `main.py` → `cli.main()`; exit codes 0/1/130 are set in `cli.py`.
- `docs/bmad-plan.md` is the phase board and prompt-logging protocol — read it before changing process or scope.
- Dataset resolution order is coded in `config.py`: `--data` > `data/sms_spam_collection.csv` > built-in 23-row fallback.
- Tests: `tests/test_pipeline.py` + `tests/test_definition_of_done.py` (92, deterministic, offline).

## Running and verifying

- `uv run python -m pytest -q` — 92 passed in ~3s. Never invoke `python` directly: on this machine it is a Microsoft Store stub that fails, so always prefix with `uv run`.
- `uv run python main.py --no-loop` for non-interactive runs — bare `main.py` blocks on the `sms>` stdin loop.
- DoD also requires `uv run python -m compileall main.py cli.py config.py dataset.py model.py evaluate.py tests` to be clean.
- `.venv` was made with `uv venv` then `uv pip install -r requirements.txt`; recreate identically if it disappears.

## Conventions that differ from defaults

- Folders are kebab-case (`design-artifacts/`), Python modules snake_case — don't create `spam_detector`-style directories.
- Type hints on public APIs and docstrings on public functions are DoD gates; no `print` debugging.

## Known pitfalls

- No dataset file means a DEMO warning banner and ~0.6 accuracy — expected, not a regression; pass `--data` for real numbers.
- The label contract is `SPAM = 1` / `HAM = 0` (`config.py`) — positive-class metrics assume it.
- Sibling `meme-classifier/` is a separate project with its own plan; phase 4 is not tracked here.

<!-- /bmad:context -->

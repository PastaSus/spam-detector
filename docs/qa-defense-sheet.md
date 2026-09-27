# Professor Q&A Sheet — spam-detector (Project B)

One row per anticipated question. Each answer cites the requirement (FR/AD/NFR)
or the test that proves it.

| # | Question | Answer · citation |
|---|---|---|
| 1 | Why is accuracy only 60%? | Honest demo-data number: 23 built-in rows, 5 test samples. Pass the real collection via `--data` for benchmark numbers. Demo banner says so (NFR-B2). |
| 2 | Why MultinomialNB? | Lab reference implementation, FR-B1; Logistic Regression shipped as the lab's permitted alternative (`--classifier lr`, `test_logistic_regression_alternative`). |
| 3 | Is the split fair / reproducible? | Stratified, `random_state=42` (FR-B3, NFR-B1); determinism asserted (`test_split_is_stratified_and_deterministic`). Reruns print identical metrics. |
| 4 | What do the metrics mean? | `accuracy_score` + `classification_report` (precision/recall/F1) + 2×2 `confusion_matrix`, rows = actual, cols = predicted (FR-B4, `test_evaluation_metrics`). |
| 5 | What if the dataset file is missing? | Warns and falls back to built-in data, never crashes (NFR-B2; `test_missing_file_falls_back_to_builtin`, `test_cli_fallback_run_warns_and_exits_zero`). Explicit bad `--data` fails loudly instead (`test_explicit_missing_file_raises`). |
| 6 | What if the data has one class / can't stratify? | Actionable `ValueError`, no raw sklearn traceback: <4 rows, <2 classes, <2 rows/class, test-split-smaller-than-classes (AD-B4; 4 split-guard tests). |
| 7 | How does save/load work? | `--save-model` writes joblib + JSON metrics sidecar (`<stem>-metrics.json`); `--load-model` skips training and reprints stored metrics (FR-B7, AD-B5; 11 persistence tests). |
| 8 | What if the load path is wrong? | Clean message, exit 1, no traceback (`test_cli_load_model_missing_path_exits_nonzero`); corrupt sidecar likewise (`test_cli_load_model_corrupt_sidecar_exits_nonzero`). |
| 9 | Are reloaded predictions identical? | Yes (NFR-B1; `test_saved_model_round_trips_predictions`). |
| 10 | Does it work offline? | No network at runtime; suite runs offline and deterministic (NFR-B4; whole suite). |
| 11 | Unicode / EOF / Ctrl+C? | Emoji/CJK/accents/empty/RTL classify without encoding errors (`test_unicode_classifies_without_encoding_error`); EOF exits 0 with no traceback at loop and CLI level (`test_loop_eof_exits_cleanly`, `test_cli_eof_stdin_exits_zero`); Ctrl+C clean (loop test). |
| 12 | How do you prove the DoD? | `pytest` (71 green) + `compileall` clean, plus 7 meta-tests: import-cycle DAG, public-function docstrings, module/class docstrings, public hints, no `print` outside `cli.py`, prompt-log ID hygiene, compile targets (`tests/test_definition_of_done.py`). |
| 13 | Where is every FR tested? | Traceability table in `tests/test_pipeline.py` module docstring — FR-B1..B7 each map to named tests (story 4.1). |
| 14 | Is the AI process itself auditable? | Every user→AI prompt logged append-only under `<PHASE>-<NNN>` in root `PROMPTS_LOG.md` (AD-5), enforced by a meta-test. |
| 15 | Why a flat layout, not a package? | Architecture decision: single-purpose CLI case study; one-way module graph `cli → {dataset, evaluate, model} → config` plus `evaluate → model`, verified acyclic by meta-test (AD-B2). |
| 16 | Can I reproduce this in one command? | `uv run python -m pytest -q` (~3 s, 71 passed) and `uv run python main.py --no-loop` (demo run). `.venv` recreates via `uv venv` + `uv pip install -r requirements.txt`. |
| 17 | What do SPAM/HAM mean numerically? | Label contract `SPAM = 1` / `HAM = 0` (`config.py`); positive-class metrics assume it (`test_evaluation_metrics`, unicode agreement assertion). |
| 18 | What exit codes and tuning flags exist? | `0` success, `1` handled errors (missing data/model, bad split); `--classifier lr`, `--test-size`, `--save-model [PATH]` (default `models/spam-model.joblib`); TSV via `--data file.tsv`. |

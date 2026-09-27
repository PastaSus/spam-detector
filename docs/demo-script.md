# Demo Script — spam-detector (Project B)

Rehearsed walkthrough for the defense. Every expected output below was captured
from the real CLI on the built-in fallback data (no `data/sms_spam_collection.csv`
present). Timings: each step runs in ~1–3 s.

Prereqs: `.venv` from `uv venv` + `uv pip install -r requirements.txt`; all
commands prefixed with `uv run` (bare `python` is a broken Store stub here).
Paths below render with `\` separators on Windows; commands are typed with `/`.
Outputs were captured on the built-in fallback data — rerun the commands to
regenerate them if the code changes.

## 1. Dataset resolution (FR-B2, NFR-B2)

```console
$ uv run python main.py --no-loop
WARNING dataset: No dataset file found (looked for ...\data\sms_spam_collection.csv) — using built-in fallback dataset (23 rows).
================================================================
WARNING: running on the built-in DEMO dataset (23 labelled rows).
Metrics are illustrative only — pass the real SMS Spam
Collection file via --data for benchmark-quality results.
================================================================
```

Say: resolution order is `--data` > `data/sms_spam_collection.csv` > built-in
fallback (`config.py`, `resolve_dataset_path`). A missing file warns and falls
back; an explicit bad path fails loudly (`test_missing_file_falls_back_to_builtin`,
`test_explicit_missing_file_raises`).

## 2. Training + metrics (FR-B1, FR-B3, FR-B4)

Same command continues:

```console
Classifier: nb | train: 18 | test: 5

Model evaluation
----------------
Test samples : 5
Accuracy     : 0.6000 (60.0%)
...
Confusion matrix (rows = actual, cols = predicted):
                pred-HAM  pred-SPAM
    actual-HAM         2          0
   actual-SPAM         2          1
```

Say: lab-exact `Pipeline([TfidfVectorizer(lowercase=True,
stop_words="english"), MultinomialNB()])`, stratified split `random_state=42`
(deterministic — reruns print identical numbers), `accuracy_score` +
`classification_report` + `confusion_matrix`. 60% is the honest demo-data
number — say so before the professor asks (see Q&A).

## 3. Explicit dataset file (FR-B2)

```console
$ uv run python main.py --data data/sample_sms.csv --no-loop
WARNING dataset: Dropped 1 row(s) with unrecognized labels from data\sample_sms.csv
Dataset: data\sample_sms.csv (10 rows)
Classifier: nb | train: 8 | test: 2
...
Accuracy     : 1.0000 (100.0%)
```

Say: the loader tolerates CSV/TSV, `label,text` or `v1,v2` headers, and
case-varied labels (NFR-B3); the header row is dropped with a warning, not
parsed as data.

## 4. Interactive classification (FR-B5, FR-B6)

Confidence numbers below come from the fallback-trained model:

```console
$ uv run python main.py
...
Interactive mode — type a message to classify · 'quit' / 'exit' / ':q' to leave

sms> Win a free prize now!!!
  SPAM (71.1% confidence)

sms> Meeting at 10am tomorrow
  HAM (68.6% confidence)

sms> quit
Goodbye.
```

Say: label + `predict_proba()` confidence; `quit`/`exit`/`:q`, blank
re-prompt, EOF and Ctrl+C all exit cleanly (loop tests + CLI EOF test).

## 5. Save and reload (FR-B7, AD-B5)

```console
$ uv run python main.py --no-loop --save-model models/spam-model.joblib

Model saved to models\spam-model.joblib (metrics: models\spam-model-metrics.json)

$ uv run python main.py --load-model models/spam-model.joblib --no-loop
Loaded model from models/spam-model.joblib (stored metrics):

Model evaluation
----------------
Test samples : 5
Accuracy     : 0.6000 (60.0%)
... identical report, no retraining ...
```

Say: joblib pipeline plus a JSON sidecar with the producing run's metrics;
missing load path exits 1 with a clean message; reloaded predictions are
identical (round-trip test). `models/` is gitignored — regenerate, don't commit.
Clean up after the demo: `rm -rf models` (or `rmdir /s models` on Windows).

## 6. Quality gates (DoD)

```console
$ uv run python -m pytest -q
71 passed in ~3s
$ uv run python -m compileall main.py cli.py config.py dataset.py model.py evaluate.py tests
```

Say: 71 tests incl. 7 DoD meta-tests (import cycles, docstrings, hints, print
hygiene, prompt-log IDs, compile targets); full FR→test traceability table in
`tests/test_pipeline.py`.

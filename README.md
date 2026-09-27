# SMS Spam Classifier

**Project 2 — Text Classification** · University semifinals case study · BMAD-managed
_(see root `PROMPTS_LOG.md` and `docs/`)_

Pure Python + scikit-learn implementation of the lab reference pipeline:
**`TfidfVectorizer(lowercase=True, stop_words="english")` → `MultinomialNB()`**, with
stratified train/test splitting, full metrics (accuracy, precision/recall, confusion matrix),
and an interactive CLI that classifies messages you type — reporting label **and** confidence
percentage via `predict_proba()`.

## Install

```bash
cd spam-detector
pip install -r requirements.txt
```

## Usage

```bash
# automatic data resolution: --data > data/sms_spam_collection.csv > built-in fallback
python main.py

# explicit dataset (CSV/TSV, label+text columns)
python main.py --data data/sample_sms.csv

# evaluate only — no interactive prompt (useful for scripts & QA)
python main.py --no-loop

# Logistic Regression variant (lab allows Naive Bayes OR Logistic Regression)
python main.py --classifier lr

# save / reuse the trained model
python main.py --save-model
python main.py --load-model models/spam-model.joblib
```

### Sample session

```
Dataset: data/sample_sms.csv (10 rows)
Classifier: nb | train: 8 | test: 2

Model evaluation
----------------
Test samples : 2
Accuracy     : 1.0000 (100.0%)

Classification report (precision / recall / F1):
              precision    recall  f1-score   support
         HAM       1.00      1.00      1.00         1
        SPAM       1.00      1.00      1.00         1

Confusion matrix (rows = actual, cols = predicted):
                 pred-HAM  pred-SPAM
      actual-HAM         1          0
     actual-SPAM         0          1

Interactive mode — type a message to classify · 'quit' / 'exit' / ':q' to leave

sms> You've won a free prize! Claim now
  SPAM (97.4% confidence)

sms> Meeting at 10am tomorrow, see you there
  HAM (91.2% confidence)

sms> quit
Goodbye.
```

> **Honest metrics:** running without any dataset file uses the 23-row built-in demo set —
> the CLI prints a warning banner. Supply the real UCI SMS Spam Collection via `--data`
> for benchmark-quality numbers (see `data/README.md`).

## Project structure

```
spam-detector/
├── main.py          # entry point
├── cli.py           # argparse + evaluation display + interactive loop
├── config.py        # paths, split params, TF-IDF/classifier params
├── dataset.py       # fallback tuples, CSV/TSV loader → DataFrame, stratified split
├── model.py         # pipeline build/train/predict_with_confidence/save/load
├── evaluate.py      # accuracy, classification report, confusion matrix
├── conftest.py      # pytest import bootstrap
├── tests/           # QA suite (deterministic, offline)
├── data/            # sample_sms.csv + SMS Spam Collection drop spot
└── requirements.txt
```

## Implementation status (BMAD)

| Phase              | Persona         | Status                                  |
| ------------------ | --------------- | --------------------------------------- |
| Specs              | PM Agent        | Done — `docs/product-requirements.md`   |
| Design             | Architect Agent | Done — `docs/system-architecture.md`    |
| Pipeline + CLI     | Tech Lead       | Done — implemented & tested (FR-B1..B7) |
| Adversarial review | QA Agent        | Pending                                 |

## Tests

```bash
cd spam-detector
python -m pytest -q
```

# System Architecture — SMS Spam Classifier

**Project:** `spam-detector/` · **Deliverable:** Project B — Text Classification
**Author:** Architect Agent · **Status:** Baseline v1.0 · **Date:** 2026-09-27
**Companion (this folder):** `product-requirements.md` (FR IDs referenced throughout) · `bmad-plan.md`
**Sibling project architecture:** `../../meme-classifier/docs/system-architecture.md`

---

## 1. Global Decisions

| # | Decision | Rationale |
|---|---|---|
| AD-1 | **Kebab-case folders** (`meme-classifier/`, `spam-detector/`, `docs/`); **snake_case modules** (`dataset.py`, `model.py`) | Explicit project convention; hyphens are illegal in Python identifiers, so importable module *files* stay snake_case (PEP 8) |
| AD-2 | **Flat module layout** inside each project (no nested package) | Small scope; `main.py` runs from project root; `conftest.py` fixes pytest imports |
| AD-3 | Shared patterns across projects: `config.py` (constants) → domain modules → `cli.py` (argparse) → `main.py` (entry) | Consistent, reviewable structure |
| AD-4 | ML logic isolated behind small modules (`dataset`, `model`, `evaluate`); no module imports `cli` | QA can test data loading, training, and metrics headlessly and deterministically |
| AD-5 | All AI prompts append-only logged in root `PROMPTS_LOG.md` | Professor requirement |

---

## 2. Project B — `spam-detector/`

### 2.1 Module Map

```
spam-detector/
├── main.py            # entry point
├── cli.py             # argparse + evaluation display + interactive loop  [FR-B4..B7]
├── config.py          # paths, split params, vectorizer/classifier params, RANDOM_STATE
├── dataset.py         # fallback tuples, CSV/TSV loader → DataFrame, stratified split [FR-B2, B3]
├── model.py           # build_pipeline / train / predict_with_confidence / save / load [FR-B1, B5]
├── evaluate.py        # accuracy, classification report, confusion matrix → printable [FR-B4]
├── conftest.py        # pytest sys.path bootstrap
├── tests/
│   └── test_pipeline.py
├── data/
│   ├── README.md      # how to obtain the UCI SMS Spam Collection file
│   └── sample_sms.csv # small demo CSV (label,text)
├── docs/              # PRD, this architecture doc, BMAD plan (agent context root)
├── requirements.txt   # scikit-learn, pandas, numpy, joblib, pytest
└── README.md
```

**Dependency rule:** `main → cli → {dataset, model, evaluate} → config` ( `model` never imports `cli`).

### 2.2 Data Flow

```
                 ┌─ explicit --data path ─┐
   loader ───────┼─ data/sms_spam_collection.csv (if present) ─┼─▶ DataFrame[text, label:int]
                 └─ FALLBACK_DATASET (built-in 23 tuples) ─────┘
                                     │
                       train_test_split(stratify=y, random_state=42)
                                     │
                    ┌────────────────┴─────────────────┐
             Pipeline.fit(X_train, y_train)      evaluate(X_test, y_test)
             Tfidf(lowercase, eng-stopwords)      accuracy_score / classification_report
             + MultinomialNB (default)            / confusion_matrix  ──▶ printed report
                                     │
                     interactive loop: input() ─▶ predict_with_confidence
                                     │            (label + predict_proba % )  [FR-B5]
                                     └─▶ "SPAM (93.2% confidence)"  |  quit/exit/:q/EOF ─▶ 0
```

### 2.3 Key Decisions

- **AD-B1 — Label contract:** internal labels are `int` (`1=spam`, `0=ham`); display labels are
  strings. `dataset.normalize_label()` maps `spam/ham/1/0/SPAM/HAM` → int; unmappable rows are
  dropped with a warning count (handles UCI header rows like `v1,v2`).
- **AD-B2 — File sniffing:** `.tsv` → tab separator, else comma; first two columns used
  (`label,text`), so both raw UCI and headered exports load (NFR-B3).
- **AD-B3 — Confidence:** `predict_proba()[0]` mapped through `pipeline.classes_` (never assume
  column order), returned as `(label_str, confidence_pct)`.
- **AD-B4 — Determinism:** `RANDOM_STATE=42`, `TEST_SIZE=0.2`, stratify always on (fails fast
  with an actionable message if a split is impossible).
- **AD-B5 — Persistence:** optional joblib `save_model`/`load_model`; loading skips retraining
  but still prints stored metrics when available (FR-B7).
- **AD-B6 — Small-data honesty:** CLI prints a warning banner when running on the built-in
  fallback so nobody mistakes demo metrics for benchmark results.

### 2.4 Interactive Loop Contract (FR-B6)

| Input | Behavior |
|---|---|
| any text | classify → `SPAM/HAM (NN.N% confidence)` |
| `` (empty) | re-prompt, no classification |
| `quit` / `exit` / `:q` | exit code 0 |
| EOF (Ctrl+D) / Ctrl+C | clean goodbye, exit code 0 — never a traceback |

---

## 3. Testing Strategy (QA Agent hand-off)

| Layer | Tests | TF needed? |
|---|---|---|
| dataset | fallback shape/labels, CSV round-trip, header row dropped, unmappable row warned | No |
| model/evaluate | pipeline structure, proba sums to 1, label ∈ {0,1}, report keys, confusion-matrix shape | No |
| adversarial (QA) | stdin EOF, single-class data, missing dataset file, unicode message text | No |

**Exit criteria:** `python -m compileall` clean · `pytest` green · no circular imports · type hints
on public APIs · every FR traceable to ≥1 test.

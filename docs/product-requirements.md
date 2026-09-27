# Product Requirements Document (PRD) — SMS Spam Classifier

**Project:** `spam-detector/` · **Deliverable:** Project B — Text Classification
**Author:** PM Agent · **Status:** Baseline v1.0 · **Date:** 2026-09-27
**Source of truth:** Lab reference sheet (encoded verbatim in root `PROMPTS_LOG.md` → INIT-001)
**Companion docs (this folder):** `system-architecture.md` · `bmad-plan.md`
**Sibling project PRD:** `../../meme-classifier/docs/product-requirements.md`

---

## 1. Product Overview

**SMS Spam Classifier** is the *Text Classification* deliverable of a two-project university
semifinals case study. It implements the lab's TF-IDF + Naive Bayes pipeline, reports standard
classification metrics, and lets the user evaluate arbitrary messages interactively.

The companion deliverable — **Meme & Reaction Image Organizer** (`meme-classifier/`), the
*Image Detection* project — has its own PRD in `meme-classifier/docs/`.

This project must run as a CLI program, be modular enough for code review, and be defensible
in a professor Q&A session.

---

## 2. Project B — SMS Spam Classifier

### 2.1 Problem
Detect whether an SMS is spam (1) or ham (0) using the lab's reference pipeline, report standard
classification metrics, and let the user evaluate arbitrary messages interactively.

### 2.2 Functional Requirements
- **FR-B1:** Build `Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])` exactly as specified; expose Logistic Regression as an optional alternate classifier (lab allows "Naive Bayes **or** Logistic Regression").
- **FR-B2:** Load data from (a) an explicit path, (b) the SMS Spam Collection file if present, or (c) a **built-in fallback dataset** of labelled tuples — `1 = spam`, `0 = ham` — into a **Pandas DataFrame**. Fallback must include the lab's four spam families (prize claims, urgent account notices, work-from-home offers, free vacation claims) and three ham families (meeting reminders, project updates, casual conversation).
- **FR-B3:** Split with `train_test_split(..., stratify=y, random_state=42)`.
- **FR-B4:** Evaluate with `accuracy_score`, `classification_report` (precision/recall/F1), and `confusion_matrix`; print all three.
- **FR-B5:** Predict label **and confidence percentage** via `predict_proba()`.
- **FR-B6:** Interactive CLI loop: read a message from stdin → print `SPAM/HAM (NN.N% confidence)`; commands `quit`/`exit`/`:q` and EOF terminate cleanly; blank input re-prompts.
- **FR-B7:** Optional `--save-model` / `--load-model` persistence (joblib) to skip retraining.

### 2.3 Non-Functional Requirements
- **NFR-B1:** Deterministic results (`random_state=42`).
- **NFR-B2:** Graceful degradation: never crash on a missing dataset file — fall back and warn.
- **NFR-B3:** Dataset loader must tolerate CSV/TSV, `label,text` or `v1,v2` headers, and case-varied labels.
- **NFR-B4:** Works offline; no network access at runtime.

### 2.4 Acceptance Criteria
1. `python main.py` with no dataset file trains on the fallback data, prints accuracy/precision/recall + a 2×2 confusion matrix, then enters the prompt loop.
2. Typing `Congratulations, you won a prize! Claim now` returns `SPAM` with a confidence > 50%.
3. Typing `Meeting at 10am tomorrow, see you there` returns `HAM`.
4. `quit` exits with code 0; `Ctrl+C`/EOF are handled without a traceback.
5. With the real SMS Spam Collection file supplied via `--data`, metrics print without code changes.

---

## 3. Lab Reference Traceability (Project B)

| Lab reference requirement | FR |
|---|---|
| `TfidfVectorizer(lowercase=True, stop_words="english")` + `MultinomialNB()` | FR-B1 |
| Labelled tuples `1=spam, 0=ham` | FR-B2 |
| Sample spam/ham families | FR-B2 |
| `predict_proba()` label + confidence % | FR-B5 |
| SMS Spam Collection file **or** built-in fallback → Pandas DataFrame | FR-B2 |
| `train_test_split` with stratification | FR-B3 |
| `accuracy_score`, `classification_report`, `confusion_matrix` | FR-B4 |
| Interactive CLI prediction loop | FR-B6 |

## 4. Out of Scope (explicitly)
- Training a production-grade spam classifier beyond the lab's TF-IDF + Naive Bayes scope; hyperparameter tuning at scale.
- Web UI / HTTP API, database integration, mobile deployment.
- Real-time or streaming message ingestion.

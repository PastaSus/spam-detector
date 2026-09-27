---
stepsCompleted: ["1", "2", "3", "4"]
inputDocuments:
  - docs/product-requirements.md
  - docs/system-architecture.md
  - docs/bmad-plan.md
---

# spam-detector - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for spam-detector, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-B1: Build `Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])` exactly as specified; expose Logistic Regression as an optional alternate classifier (lab allows "Naive Bayes **or** Logistic Regression").

FR-B2: Load data from (a) an explicit path, (b) the SMS Spam Collection file if present, or (c) a built-in fallback dataset of labelled tuples — `1 = spam`, `0 = ham` — into a Pandas DataFrame. Fallback must include the lab's four spam families (prize claims, urgent account notices, work-from-home offers, free vacation claims) and three ham families (meeting reminders, project updates, casual conversation).

FR-B3: Split with `train_test_split(..., stratify=y, random_state=42)`.

FR-B4: Evaluate with `accuracy_score`, `classification_report` (precision/recall/F1), and `confusion_matrix`; print all three.

FR-B5: Predict label **and confidence percentage** via `predict_proba()`.

FR-B6: Interactive CLI loop: read a message from stdin → print `SPAM/HAM (NN.N% confidence)`; commands `quit`/`exit`/`:q` and EOF terminate cleanly; blank input re-prompts.

FR-B7: Optional `--save-model` / `--load-model` persistence (joblib) to skip retraining.

### NonFunctional Requirements

NFR-B1: Deterministic results (`random_state=42`).

NFR-B2: Graceful degradation: never crash on a missing dataset file — fall back and warn.

NFR-B3: Dataset loader must tolerate CSV/TSV, `label,text` or `v1,v2` headers, and case-varied labels.

NFR-B4: Works offline; no network access at runtime.

### Additional Requirements

From `docs/system-architecture.md`:

- **AD-1:** Kebab-case folders, snake_case module files (hyphens are illegal in Python identifiers).
- **AD-2:** Flat module layout inside the project (no nested package); `main.py` runs from project root; `conftest.py` fixes pytest imports.
- **AD-3:** Shared pattern `config.py` (constants) → domain modules → `cli.py` (argparse) → `main.py` (entry).
- **AD-4:** ML logic isolated behind small modules (`dataset`, `model`, `evaluate`); no module except `cli` is imported by them — specifically `model` never imports `cli`.
- **AD-5:** All AI prompts append-only logged in root `PROMPTS_LOG.md` (Professor requirement).
- **AD-B1:** Label contract — internal labels are `int` (`1=spam`, `0=ham`); display labels are strings; `dataset.normalize_label()` maps `spam/ham/1/0/SPAM/HAM` → int; unmappable rows dropped with a warning count.
- **AD-B2:** File sniffing — `.tsv` → tab separator, else comma; first two columns used (`label,text`) so both raw UCI and headered exports load.
- **AD-B3:** Confidence — `predict_proba()[0]` mapped through `pipeline.classes_` (never assume column order), returned as `(label_str, confidence_pct)`.
- **AD-B4:** Determinism — `RANDOM_STATE=42`, `TEST_SIZE=0.2`, stratify always on; fail fast with an actionable message if a split is impossible.
- **AD-B5:** Persistence — optional joblib `save_model`/`load_model`; loading skips retraining but still prints stored metrics when available.
- **AD-B6:** Small-data honesty — CLI prints a warning banner when running on the built-in fallback.
- **Dependency rule:** `main → cli → {dataset, model, evaluate} → config`.
- **Exit criteria (Testing Strategy):** `python -m compileall` clean · `pytest` green · no circular imports · type hints on public APIs · every FR traceable to ≥1 test.
- **Definition of Done (bmad-plan §3):** docstrings on public functions; no `print` debugging; adversarial cases covered (stdin EOF, single-class data, missing dataset file, unstratifiable data).
- **No starter template** is specified in Architecture; no infrastructure, deployment, API versioning, monitoring, or data-migration requirements — CLI, offline, single-machine.
- **Out of scope (PRD §4):** production-grade tuning, web UI / HTTP API, database integration, mobile deployment, real-time/streaming ingestion.

### UX Design Requirements

None — this is a CLI-only project with no UX design contract. `design_artifacts/` (WDS A–E) is empty and `design_system_mode` is `none`. The interactive-loop contract in `system-architecture.md` §2.4 governs terminal UX instead.

### FR Coverage Map

FR-B1: Epic 1 — reference TF-IDF + MultinomialNB pipeline (+ LR alternate)
FR-B2: Epic 1 — explicit path / UCI file / built-in fallback → DataFrame
FR-B3: Epic 1 — stratified deterministic train/test split
FR-B4: Epic 1 — accuracy, classification report, confusion matrix printed
FR-B5: Epic 2 — label + confidence % via `predict_proba()`
FR-B6: Epic 2 — interactive stdin loop, quit/exit/:q/EOF, blank re-prompt
FR-B7: Epic 3 — optional joblib save / load to skip retraining

NFR-B1: Epic 1 · NFR-B2: Epic 1 · NFR-B3: Epic 1 · NFR-B4: Epic 1, Epic 2, Epic 4
Additional Requirements: Epic 1 (AD-1..AD-4, AD-B1..AD-B4, AD-B6), Epic 2 (interactive-loop contract §2.4, AD-B3), Epic 3 (AD-B5), Epic 4 (AD-5, exit criteria, DoD adversarial cases, phases 5–6)

## Epic List

> **File-churn check (step 4.4):** Epics 1–3 all edit `cli.py`/`model.py`. Consolidation was
> considered and rejected: each epic is a separately demonstrable user outcome (evaluate →
> interact → persist), Epic 3 and Epic 4 must each run without work from epics after them, and
> splitting keeps every story inside one dev session's context. Overlap is incidental sharing of
> a small flat codebase, not churn from a feedback loop.

### Epic 1: Train and Evaluate the Classifier
The user can point the CLI at a dataset (or rely on the shipped fallback), train the lab's reference pipeline, and read a complete metrics report — accuracy, precision/recall/F1, and a 2×2 confusion matrix — with honest demo-data warnings and repeatable numbers every run.
**FRs covered:** FR-B1, FR-B2, FR-B3, FR-B4

### Epic 2: Classify Messages Interactively
After evaluation, the user can type arbitrary messages at the `sms>` prompt and get back `SPAM/HAM` with a confidence percentage, re-prompt on blank input, and exit cleanly through `quit`/`exit`/`:q` or EOF without a traceback.
**FRs covered:** FR-B5, FR-B6

### Epic 3: Save and Reload the Trained Model
The user can persist a trained model with `--save-model` and skip retraining on later runs with `--load-model`, still seeing the stored metrics from the run that produced it.
**FRs covered:** FR-B7

### Epic 4: Adversarial Hardening and Defense Readiness
The Tech Lead can defend the deliverable: every FR traced to at least one test, adversarial cases covered (stdin EOF, single-class data, missing dataset file, unstratifiable data, unicode), exit criteria green, prompts logged, plus the demo script and professor Q&A sheet required by project phases 5–6.
**FRs covered:** none directly — carries the Additional Requirements, NFR-B4 evidence, and bmad-plan phases 5 and 6

## Epic 1: Train and Evaluate the Classifier

The user can point the CLI at a dataset (or rely on the shipped fallback), train the lab's reference pipeline, and read a complete metrics report — accuracy, precision/recall/F1, and a 2×2 confusion matrix — with honest demo-data warnings and repeatable numbers every run.

**FRs covered:** FR-B1, FR-B2, FR-B3, FR-B4 · **NFRs:** NFR-B1, NFR-B2, NFR-B3, NFR-B4

### Story 1.1: Scaffold the Flat Module Layout and Configuration

As a developer,
I want the agreed module layout and all tunable constants centralised in `config.py`,
So that every later story imports one source of truth instead of hard-coding values.

**Acceptance Criteria:**

**Given** the project root
**When** the layout is inspected
**Then** `main.py`, `cli.py`, `config.py`, `dataset.py`, `model.py`, `evaluate.py`, `conftest.py`, and `tests/` exist at the root (AD-1, AD-2)
**And** folders are kebab-case while module files are snake_case

**Given** `config.py`
**When** its public constants are read
**Then** they expose `RANDOM_STATE = 42`, `TEST_SIZE = 0.2`, `TFIDF_PARAMS = {"lowercase": True, "stop_words": "english"}`, `CLASSIFIERS`, `DEFAULT_CLASSIFIER`, path constants, and the label contract `SPAM = 1` / `HAM = 0` (AD-B4)
**And** no other module re-declares those values

**Given** `conftest.py`
**When** pytest starts from the project root
**Then** the project root is on `sys.path` so flat imports resolve (AD-2)

### Story 1.2: Load Datasets From File or Built-in Fallback

As a user,
I want the classifier to find data without me configuring anything,
So that the program still runs and explains itself when the real dataset is missing.

**Acceptance Criteria:**

**Given** no dataset file exists on disk
**When** the loader resolves a dataset (FR-B2)
**Then** it returns a Pandas DataFrame built from the 23-row built-in fallback containing the four lab spam families and three ham families
**And** it emits a warning that the built-in data is being used (NFR-B2)

**Given** an explicit `--data` path to a CSV or TSV
**When** the loader runs
**Then** the first two columns are read as label and text and converted to `int` labels (AD-B2)

**Given** a file with `v1,v2` headers, mixed-case labels (`spam`/`HAM`/`1`/`0`), or unparseable rows (NFR-B3)
**When** the loader runs
**Then** header rows and unmappable rows are dropped with a warning count instead of raising (AD-B1)

**Given** a path that does not exist
**When** the loader runs
**Then** it falls back to the built-in dataset and warns rather than crashing (NFR-B2)

### Story 1.3: Train the Reference Pipeline With a Deterministic Split

As a user,
I want the lab's exact TF-IDF → Naive Bayes pipeline trained on a stratified split,
So that results are reproducible and defensible against the reference sheet.

**Acceptance Criteria:**

**Given** a loaded DataFrame
**When** the pipeline is built (FR-B1)
**Then** it is `Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])`
**And** `--classifier lr` swaps in `LogisticRegression` while `nb` remains the default

**Given** labelled data
**When** the split runs (FR-B3)
**Then** it is `train_test_split(..., stratify=y, random_state=42)`
**And** repeated runs produce identical splits (NFR-B1)

**Given** a dataset with a single class
**When** the split is attempted
**Then** it fails fast with an actionable message instead of a stack trace (AD-B4)

**Given** any run
**When** the modules import each other
**Then** the dependency direction is `main → cli → {dataset, model, evaluate} → config` and no module imports `cli` (AD-4)
**And** no network access occurs at runtime (NFR-B4)

### Story 1.4: Evaluate and Print the Full Metrics Report

As a user,
I want accuracy, precision/recall/F1, and a confusion matrix printed after training,
So that I can judge the model before trusting it interactively.

**Acceptance Criteria:**

**Given** a trained model and held-out test data
**When** evaluation runs (FR-B4)
**Then** `accuracy_score`, `classification_report`, and `confusion_matrix` are all computed and printed
**And** the confusion matrix is rendered as a 2×2 grid with `pred-HAM`/`pred-SPAM` columns

**Given** the built-in fallback dataset
**When** the report prints
**Then** a demo-data warning banner is shown so the metrics are not mistaken for benchmark results (AD-B6)

**Given** the real SMS Spam Collection supplied via `--data`
**When** the same code path runs
**Then** metrics print with no code changes (acceptance criterion 5)

**Given** `--no-loop`
**When** the CLI runs
**Then** it prints the evaluation and exits with code 0 without waiting on stdin

## Epic 2: Classify Messages Interactively

After evaluation, the user can type arbitrary messages at the `sms>` prompt and get back `SPAM/HAM` with a confidence percentage, re-prompt on blank input, and exit cleanly through `quit`/`exit`/`:q` or EOF without a traceback.

**FRs covered:** FR-B5, FR-B6

### Story 2.1: Return a Label and Confidence for One Message

As a user,
I want each prediction to carry a confidence percentage,
So that I can tell a borderline message from an obvious one.

**Acceptance Criteria:**

**Given** a trained pipeline
**When** a single message is predicted (FR-B5)
**Then** `predict_proba()` supplies both the label and a confidence percentage
**And** the probability column is resolved through `pipeline.classes_` rather than assumed positional order (AD-B3)

**Given** any prediction
**When** the result is unpacked
**Then** it is `(label_str, confidence_pct)` with the label drawn from the `1 = spam` / `0 = ham` contract (AD-B1)
**And** the probabilities sum to 1.0 across `HAM` and `SPAM`

### Story 2.2: Run the Interactive Loop With Clean Exits

As a user,
I want a prompt where I can type messages and quit whenever I like,
So that I can classify ad-hoc texts without restarting the program.

**Acceptance Criteria:**

**Given** the interactive session is active (FR-B6)
**When** I type a message
**Then** the output is `SPAM/HAM (NN.N% confidence)`
**And** `Congratulations, you won a prize! Claim now` returns `SPAM` with confidence > 50% while `Meeting at 10am tomorrow, see you there` returns `HAM`

**Given** the prompt
**When** I enter an empty line
**Then** the prompt re-appears with no classification performed

**Given** the prompt
**When** I enter `quit`, `exit`, or `:q`, or the stream hits EOF / Ctrl+C
**Then** the program exits with code 0 and a goodbye, never a traceback

**Given** stdin is closed immediately (EOF with no input)
**When** the loop starts
**Then** it terminates cleanly with exit code 0

## Epic 3: Save and Reload the Trained Model

The user can persist a trained model with `--save-model` and skip retraining on later runs with `--load-model`, still seeing the stored metrics from the run that produced it.

**FRs covered:** FR-B7

### Story 3.1: Persist the Trained Model and Its Metrics

As a user,
I want to save a trained model to disk,
So that I do not pay for retraining on every run.

**Acceptance Criteria:**

**Given** a trained model
**When** `--save-model` is passed (FR-B7)
**Then** the pipeline is serialised with joblib to `models/spam-model.joblib`
**And** the metrics from the run that produced it are stored alongside it (AD-B5)

**Given** `models/` does not exist
**When** saving runs
**Then** the directory is created and the save completes without error

### Story 3.2: Reload a Saved Model Without Retraining

As a user,
I want `--load-model` to reuse a previous model,
So that subsequent runs start instantly.

**Acceptance Criteria:**

**Given** a previously saved model file
**When** `--load-model models/spam-model.joblib` is passed (FR-B7)
**Then** training is skipped and the stored metrics are still printed when available (AD-B5)

**Given** a `--load-model` path that does not exist
**When** the CLI starts
**Then** it reports the problem clearly and exits non-zero rather than raising a raw traceback

**Given** a saved model
**When** it is used for prediction
**Then** outputs are identical to the run that saved it (NFR-B1)

## Epic 4: Adversarial Hardening and Defense Readiness

The Tech Lead can defend the deliverable: every FR traced to at least one test, adversarial cases covered (stdin EOF, single-class data, missing dataset file, unstratifiable data, unicode), exit criteria green, prompts logged, plus the demo script and professor Q&A sheet required by project phases 5–6.

**FRs covered:** none directly — carries the Additional Requirements, NFR-B4 evidence, and bmad-plan phases 5 and 6

### Story 4.1: Cover Every FR With Automated Tests

As a QA agent,
I want a deterministic offline test suite that traces to each FR,
So that the exit criteria "every FR traceable to at least one test" can be demonstrated.

**Acceptance Criteria:**

**Given** the test suite
**When** it runs offline with `pytest`
**Then** it is green and deterministic (`random_state=42`, no network)
**And** dataset, pipeline-structure, probability, and metrics assertions each exist

**Given** FR-B1 through FR-B7
**When** the traceability is reviewed
**Then** each has at least one passing test

### Story 4.2: Attack the Edge Cases

As a QA agent,
I want adversarial tests for the failure modes the lab and DoD name,
So that surprises surface before the defense, not during it.

**Acceptance Criteria:**

**Given** a missing dataset file
**When** the pipeline runs
**Then** it falls back and warns instead of crashing (NFR-B2)

**Given** a single-class or otherwise unstratifiable dataset
**When** the split runs
**Then** the failure is handled with an actionable message (AD-B4)

**Given** an EOF-terminated stdin
**When** the interactive loop runs
**Then** it exits 0 without a traceback (FR-B6)

**Given** unicode message text
**When** it is classified
**Then** prediction succeeds and no encoding error is raised

### Story 4.3: Prove the Definition of Done

As a Tech Lead,
I want machine-checkable evidence for each DoD gate,
So that sign-off rests on commands, not assertions.

**Acceptance Criteria:**

**Given** the source tree
**When** `uv run python -m compileall main.py cli.py config.py dataset.py model.py evaluate.py tests` runs
**Then** it exits clean

**Given** `uv run python -m pytest -q`
**When** it runs
**Then** the whole suite passes

**Given** the module graph
**When** imports are inspected
**Then** there are no circular imports, public APIs carry type hints, public functions carry docstrings, and no `print` debugging remains

**Given** root `PROMPTS_LOG.md`
**When** it is reviewed
**Then** every user→AI prompt has an append-only `<PHASE>-<NNN>` row (AD-5)

### Story 4.4: Assemble the Demo Script and Q&A Sheet

As a Tech Lead,
I want a rehearsed demo script and a professor Q&A sheet,
So that phases 5 and 6 close with a defensible presentation.

**Acceptance Criteria:**

**Given** the finished CLI
**When** the demo script is followed
**Then** it walks dataset resolution, training, metrics, interactive classification, and save/load with expected outputs

**Given** the PRD, architecture, and test suite
**When** the Q&A sheet is written
**Then** each anticipated question cites the FR/AD or test that answers it

**Given** phases 5 and 6
**When** their artifacts exist, prompts are logged, and the Tech Lead signs off
**Then** the phase board in `docs/bmad-plan.md` may be updated — and not before

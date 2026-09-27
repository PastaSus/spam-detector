# Epic 3 Context: Save and Reload the Trained Model

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Let users persist a trained classifier and reuse it on later runs without retraining, while still showing the metrics from the run that produced it. Note: only the epics file was available — no separate PRD, architecture, or design artifacts were found — so this context is distilled from the epic breakdown alone.

## Stories

- Story 3.1: Persist the Trained Model and Its Metrics
- Story 3.2: Reload a Saved Model Without Retraining

## Requirements & Constraints

- Provide opt-in save and load flags so retraining can be skipped on subsequent runs.
- Saved bundle must include both the trained pipeline and the metrics from the producing run; loading must display those stored metrics when available.
- Saving must create the target directory if absent and default to `models/spam-model.joblib`.
- A missing load path must fail with a clear message and non-zero exit, never a raw traceback.
- Reloaded predictions must be identical to the run that saved the model.
- Must work offline with no network access.

## Technical Decisions

- Serialize with joblib to a single `models/spam-model.joblib` artifact holding the fitted pipeline plus its metrics payload.
- Load path bypasses dataset loading, splitting, and training entirely, then reuses the same prediction and metrics-display code paths.
- Keep persistence helpers in the model layer behind small save/load functions; wire flags through the CLI layer only, preserving one-way dependencies toward shared constants.

## Cross-Story Dependencies

- Story 3.2 depends on the artifact produced by Story 3.1; both build on the trained pipeline from Epic 1.

"""Pipeline construction, training, prediction, and persistence (FR-B1, FR-B5, FR-B7).

Lab reference implementation:
    Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])
with Logistic Regression available as the lab's permitted alternative.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from config import CLASSIFIERS, DEFAULT_CLASSIFIER, SPAM, TFIDF_PARAMS

logger = logging.getLogger(__name__)


def build_pipeline(classifier: str = DEFAULT_CLASSIFIER) -> Pipeline:
    """Build the TF-IDF + classifier pipeline exactly as specified by the lab sheet."""
    if classifier == "nb":
        estimator = MultinomialNB()
    elif classifier == "lr":
        estimator = LogisticRegression(max_iter=1000)
    else:
        raise ValueError(f"Unknown classifier {classifier!r}; choose from {CLASSIFIERS}")
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
            ("clf", estimator),
        ]
    )


def train(pipeline: Pipeline, X_train: pd.Series, y_train: pd.Series) -> Pipeline:
    """Fit the pipeline on the training corpus and return it."""
    pipeline.fit(X_train, y_train)
    logger.debug("Trained pipeline on %d samples", len(X_train))
    return pipeline


def display_label(label: int) -> str:
    """Render a label int as SPAM/HAM."""
    return "SPAM" if int(label) == SPAM else "HAM"


def predict_label(pipeline: Pipeline, text: str) -> int:
    """Return the raw predicted label (1 = spam, 0 = ham)."""
    return int(pipeline.predict([text])[0])


def predict_with_confidence(pipeline: Pipeline, text: str) -> tuple[str, float]:
    """Return ``(label_str, confidence_pct)`` using predict_proba (FR-B5).

    Class order is read from ``pipeline.classes_`` — column position is never assumed.
    """
    probabilities = pipeline.predict_proba([text])[0]
    classes = list(pipeline.classes_)
    best_index = max(range(len(classes)), key=lambda i: probabilities[i])
    label = int(classes[best_index])
    confidence = float(probabilities[best_index]) * 100.0
    return display_label(label), confidence


def metrics_path_for(path: Path | str) -> Path:
    """Return the JSON sidecar path holding a saved model's metrics (FR-B7)."""
    target = Path(path)
    return target.with_name(f"{target.stem}-metrics.json")


def save_model(
    pipeline: Pipeline,
    path: Path | str,
    metrics: Mapping[str, Any] | None = None,
) -> Path:
    """Persist the trained pipeline with joblib (FR-B7).

    When ``metrics`` is given, the mapping must be JSON-serializable and is
    also written to the sidecar from :func:`metrics_path_for`, so the metrics
    of the run that produced the model travel with the model file.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Serialise first so a bad mapping fails before any file is written.
    payload = json.dumps(dict(metrics), indent=2) + "\n" if metrics is not None else None
    joblib.dump(pipeline, target)
    logger.info("Model saved to %s", target)
    if payload is not None:
        sidecar = metrics_path_for(target)
        sidecar.write_text(payload, encoding="utf-8")
        logger.info("Metrics saved to %s", sidecar)
    return target


def load_model(path: Path | str) -> Pipeline:
    """Load a previously saved pipeline (FR-B7)."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Model file not found: {source}")
    pipeline = joblib.load(source)
    logger.info("Model loaded from %s", source)
    return pipeline


def load_metrics(model_path: Path | str) -> dict[str, Any]:
    """Read the stored metrics sidecar for a saved model (FR-B7).

    Returns an empty dict when no sidecar exists, so callers treat missing
    metrics as "not available" rather than an error.
    """
    sidecar = metrics_path_for(model_path)
    if not sidecar.is_file():
        return {}
    return json.loads(sidecar.read_text(encoding="utf-8"))

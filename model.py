"""Pipeline construction, training, prediction, and persistence (FR-B1, FR-B5, FR-B7).

Lab reference implementation:
    Pipeline([TfidfVectorizer(lowercase=True, stop_words="english"), MultinomialNB()])
with Logistic Regression available as the lab's permitted alternative.
"""
from __future__ import annotations

import logging
from pathlib import Path

import joblib
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


def train(pipeline: Pipeline, X_train, y_train) -> Pipeline:
    """Fit the pipeline on the training corpus and return it."""
    pipeline.fit(X_train, y_train)
    logger.debug("Trained pipeline on %d samples", len(X_train))
    return pipeline


def display_label(label: int) -> str:
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


def save_model(pipeline: Pipeline, path: Path | str) -> Path:
    """Persist the trained pipeline with joblib (FR-B7)."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, target)
    logger.info("Model saved to %s", target)
    return target


def load_model(path: Path | str) -> Pipeline:
    """Load a previously saved pipeline (FR-B7)."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Model file not found: {source}")
    pipeline = joblib.load(source)
    logger.info("Model loaded from %s", source)
    return pipeline

"""Model evaluation: accuracy, precision/recall report, confusion matrix (FR-B4).

Uses sklearn's accuracy_score, classification_report, and confusion_matrix
exactly as required by the lab reference sheet.
"""
from __future__ import annotations

from dataclasses import dataclass

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from config import HAM, SPAM
from model import display_label

LABELS = [HAM, SPAM]
TARGET_NAMES = [display_label(HAM), display_label(SPAM)]  # ["HAM", "SPAM"]


@dataclass(frozen=True)
class EvaluationReport:
    """Bundle of every metric the lab requires."""

    accuracy: float
    classification_report: str  # formatted sklearn text report
    confusion_matrix: list[list[int]]  # fixed 2x2, rows = actual, cols = predicted
    n_test: int

    @property
    def accuracy_pct(self) -> float:
        return self.accuracy * 100.0


def evaluate(pipeline, X_test, y_test) -> EvaluationReport:
    """Compute accuracy, classification report, and 2x2 confusion matrix (FR-B4)."""
    y_pred = pipeline.predict(X_test)
    return EvaluationReport(
        accuracy=float(accuracy_score(y_test, y_pred)),
        classification_report=classification_report(
            y_test,
            y_pred,
            labels=LABELS,
            target_names=TARGET_NAMES,
            zero_division=0,
        ),
        confusion_matrix=confusion_matrix(y_test, y_pred, labels=LABELS).tolist(),
        n_test=len(y_test),
    )


def format_report(report: EvaluationReport) -> str:
    """Render the evaluation report for the CLI."""
    matrix = report.confusion_matrix
    lines = [
        "Model evaluation",
        "----------------",
        f"Test samples : {report.n_test}",
        f"Accuracy     : {report.accuracy:.4f} ({report.accuracy_pct:.1f}%)",
        "",
        "Classification report (precision / recall / F1):",
        report.classification_report.rstrip(),
        "",
        "Confusion matrix (rows = actual, cols = predicted):",
        f"{'':>14}  pred-HAM  pred-SPAM",
        f"{'actual-HAM':>14}  {matrix[0][0]:>8}  {matrix[0][1]:>9}",
        f"{'actual-SPAM':>14}  {matrix[1][0]:>8}  {matrix[1][1]:>9}",
    ]
    return "\n".join(lines)

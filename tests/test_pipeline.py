"""Unit tests for the spam-detector pipeline (no network, fully deterministic)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from config import SPAM, TFIDF_PARAMS
from dataset import (
    FALLBACK_DATASET,
    fallback_dataframe,
    load_dataset,
    normalize_label,
    resolve_dataset_path,
    split_data,
)
from evaluate import evaluate, format_report
from model import build_pipeline, predict_with_confidence, predict_label, train


class TestDataset:
    def test_fallback_dataframe_shape_and_labels(self) -> None:
        df = fallback_dataframe()

        assert list(df.columns) == ["text", "label"]
        assert len(df) == len(FALLBACK_DATASET)
        assert set(df["label"].unique()) == {0, 1}  # both classes present
        assert df["text"].str.len().min() > 0

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("spam", 1), ("SPAM", 1), ("1", 1), (1, 1),
            ("ham", 0), ("Ham", 0), ("0", 0), (0, 0),
            ("v1", None), ("label", None), ("", None), (None, None),
        ],
    )
    def test_normalize_label_variants(self, raw: object, expected: int | None) -> None:
        assert normalize_label(raw) == expected

    def test_load_dataset_from_csv_roundtrip(self, tmp_path: Path) -> None:
        csv = tmp_path / "messages.csv"
        csv.write_text(
            "label,text\n"
            "spam,\"You won a prize, claim it now\"\n"
            "ham,\"Meeting at 10am tomorrow\"\n",
            encoding="utf-8",
        )

        df = load_dataset(csv)

        assert list(df.columns) == ["text", "label"]
        assert sorted(df["label"].tolist()) == [0, 1]
        assert "prize" in df.loc[df["label"] == SPAM, "text"].iloc[0]

    def test_header_row_is_dropped_not_parsed_as_data(self, tmp_path: Path) -> None:
        csv = tmp_path / "with_header.csv"
        csv.write_text("label,text\nspam,free prize\nham,see you at noon\n", encoding="utf-8")

        df = load_dataset(csv)

        assert len(df) == 2
        assert set(df["label"]) == {0, 1}

    def test_explicit_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            resolve_dataset_path(tmp_path / "nope.csv")

    def test_missing_file_falls_back_to_builtin(self, tmp_path: Path, monkeypatch) -> None:
        import dataset as dataset_module

        monkeypatch.setattr(
            dataset_module, "SMS_SPAM_COLLECTION_PATH", tmp_path / "absent.csv"
        )

        assert resolve_dataset_path(None) is None
        df = load_dataset(None)
        assert len(df) == len(FALLBACK_DATASET)

    def test_split_is_stratified_and_deterministic(self) -> None:
        df = fallback_dataframe()

        X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)
        _, _, y_train2, _ = split_data(df, test_size=0.2, random_state=42)

        assert len(X_train) == 18 and len(X_test) == 5  # 23 rows, test_size=0.2
        assert y_train.value_counts().to_dict() == {0: 9, 1: 9}
        assert y_test.value_counts().to_dict() == {0: 2, 1: 3}  # stratified (FR-B3)
        assert y_train.tolist() == y_train2.tolist()  # deterministic (NFR-B1)

    def test_split_rejects_single_class(self) -> None:
        df = pd.DataFrame({"text": ["a", "b", "c", "d"], "label": [1, 1, 1, 1]})
        with pytest.raises(ValueError, match="at least 2 classes"):
            split_data(df)


class TestPipeline:
    def test_lab_reference_structure(self) -> None:
        pipeline = build_pipeline("nb")

        assert isinstance(pipeline, Pipeline)
        assert [name for name, _ in pipeline.steps] == ["tfidf", "clf"]
        vectorizer = pipeline.named_steps["tfidf"]
        assert vectorizer.lowercase is TFIDF_PARAMS["lowercase"] is True
        assert vectorizer.stop_words == "english"
        assert isinstance(pipeline.named_steps["clf"], MultinomialNB)

    def test_logistic_regression_alternative(self) -> None:
        pipeline = build_pipeline("lr")
        assert type(pipeline.named_steps["clf"]).__name__ == "LogisticRegression"

    def test_unknown_classifier_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown classifier"):
            build_pipeline("svm")

    @pytest.fixture()
    def trained(self):
        df = fallback_dataframe()
        X_train, X_test, y_train, y_test = split_data(df)
        pipeline = train(build_pipeline("nb"), X_train, y_train)
        return pipeline, X_test, y_test

    def test_predict_with_confidence_contract(self, trained) -> None:
        pipeline, _, _ = trained

        label, confidence = predict_with_confidence(pipeline, "Claim your free prize now!!")

        assert label in {"SPAM", "HAM"}
        assert 0.0 < confidence <= 100.0

    def test_spammy_prize_message_detected(self, trained) -> None:
        pipeline, _, _ = trained
        assert predict_label(pipeline, "You've won a prize! Claim your free gift now") == SPAM

    def test_meeting_reminder_detected_as_ham(self, trained) -> None:
        pipeline, _, _ = trained
        assert predict_label(pipeline, "Meeting at 10am tomorrow, see you there") == 0

    def test_evaluation_metrics(self, trained) -> None:
        pipeline, X_test, y_test = trained

        report = evaluate(pipeline, X_test, y_test)

        assert 0.0 <= report.accuracy <= 1.0
        assert report.n_test == len(X_test)
        assert len(report.confusion_matrix) == 2
        assert all(len(row) == 2 for row in report.confusion_matrix)
        assert "precision" in report.classification_report

        rendered = format_report(report)
        assert "Accuracy" in rendered
        assert "Confusion matrix" in rendered

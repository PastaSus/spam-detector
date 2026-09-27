"""Unit tests for the spam-detector pipeline (no network, fully deterministic).

FR traceability (story 4.1 — every FR has at least one passing test):

- FR-B1 (pipeline structure): test_lab_reference_structure,
  test_logistic_regression_alternative, test_unknown_classifier_raises
- FR-B2 (dataset loading): test_fallback_dataframe_shape_and_labels,
  test_normalize_label_variants, test_load_dataset_from_csv_roundtrip,
  test_header_row_is_dropped_not_parsed_as_data,
  test_explicit_missing_file_raises, test_missing_file_falls_back_to_builtin
- FR-B3 (deterministic split): test_split_is_stratified_and_deterministic,
  test_split_rejects_single_class
- FR-B4 (metrics report): test_evaluation_metrics
- FR-B5 (label + confidence): test_predict_with_confidence_contract,
  test_spammy_prize_message_detected, test_meeting_reminder_detected_as_ham
- FR-B6 (interactive loop): test_loop_classifies_then_quits,
  test_loop_exit_commands, test_loop_blank_input_reprompts,
  test_loop_eof_exits_cleanly, test_loop_output_format
- FR-B7 (persistence): test_metrics_path_for_derives_sidecar_name,
  test_save_model_writes_pipeline_and_metrics_sidecar,
  test_save_model_without_metrics_writes_no_sidecar,
  test_saved_model_round_trips_predictions, test_cli_save_model_passes_report,
  test_cli_load_model_prints_stored_metrics,
  test_cli_load_model_without_sidecar_skips_evaluation,
  test_cli_load_model_missing_path_exits_nonzero,
  test_load_metrics_absent_sidecar_returns_empty,
  test_cli_load_model_corrupt_sidecar_exits_nonzero,
  test_cli_load_model_ignores_missing_dataset
"""
from __future__ import annotations

import json
import logging
import re
from argparse import Namespace
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import pytest
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from cli import _interactive_loop, main, run
from config import SPAM, TEST_SIZE, TFIDF_PARAMS
from dataset import (
    FALLBACK_DATASET,
    fallback_dataframe,
    load_dataset,
    normalize_label,
    resolve_dataset_path,
    split_data,
)
from evaluate import evaluate, format_report
from model import (
    build_pipeline,
    load_metrics,
    load_model,
    metrics_path_for,
    predict_with_confidence,
    predict_label,
    save_model,
    train,
)


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


class TestPersistence:
    @pytest.fixture()
    def trained_report(self):
        df = fallback_dataframe()
        X_train, X_test, y_train, y_test = split_data(df)
        pipeline = train(build_pipeline("nb"), X_train, y_train)
        return pipeline, evaluate(pipeline, X_test, y_test)

    def test_metrics_path_for_derives_sidecar_name(self, tmp_path: Path) -> None:
        model_path = tmp_path / "models" / "spam-model.joblib"

        assert metrics_path_for(model_path) == tmp_path / "models" / "spam-model-metrics.json"

    def test_save_model_writes_pipeline_and_metrics_sidecar(
        self, trained_report, tmp_path: Path
    ) -> None:
        pipeline, report = trained_report
        model_path = tmp_path / "nested" / "spam-model.joblib"

        saved = save_model(pipeline, model_path, metrics=asdict(report))

        assert saved == model_path
        assert model_path.is_file()
        sidecar = metrics_path_for(model_path)
        assert sidecar.is_file()
        assert json.loads(sidecar.read_text(encoding="utf-8")) == asdict(report)

    def test_save_model_without_metrics_writes_no_sidecar(
        self, trained_report, tmp_path: Path
    ) -> None:
        pipeline, _ = trained_report
        model_path = tmp_path / "spam-model.joblib"

        save_model(pipeline, model_path)

        assert model_path.is_file()
        assert not metrics_path_for(model_path).exists()

    def test_saved_model_round_trips_predictions(
        self, trained_report, tmp_path: Path
    ) -> None:
        pipeline, _ = trained_report
        texts = [
            "You've won a prize! Claim your free gift now",
            "Meeting at 10am tomorrow, see you there",
        ]

        reloaded = load_model(save_model(pipeline, tmp_path / "spam-model.joblib"))

        for text in texts:
            assert predict_label(reloaded, text) == predict_label(pipeline, text)

    def test_cli_save_model_passes_report(self, tmp_path: Path) -> None:
        model_path = tmp_path / "cli-model.joblib"
        args = Namespace(
            load_model=None,
            data=None,
            test_size=TEST_SIZE,
            classifier="nb",
            save_model=str(model_path),
            no_loop=True,
        )

        assert run(args) == 0

        sidecar = metrics_path_for(model_path)
        assert json.loads(sidecar.read_text(encoding="utf-8"))["n_test"] > 0

    def test_cli_load_model_prints_stored_metrics(
        self, trained_report, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        pipeline, report = trained_report
        model_path = tmp_path / "m.joblib"
        save_model(pipeline, model_path, metrics=asdict(report))
        args = Namespace(
            load_model=str(model_path),
            data=None,
            test_size=TEST_SIZE,
            classifier="nb",
            save_model=None,
            no_loop=True,
        )

        assert run(args) == 0

        out = capsys.readouterr().out
        assert "stored metrics" in out
        assert "Accuracy" in out
        assert "Confusion matrix" in out

    def test_cli_load_model_without_sidecar_skips_evaluation(
        self, trained_report, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        pipeline, _ = trained_report
        model_path = tmp_path / "m.joblib"
        save_model(pipeline, model_path)
        args = Namespace(
            load_model=str(model_path),
            data=None,
            test_size=TEST_SIZE,
            classifier="nb",
            save_model=None,
            no_loop=True,
        )

        assert run(args) == 0

        assert "evaluation skipped" in capsys.readouterr().out

    def test_cli_load_model_missing_path_exits_nonzero(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        with caplog.at_level(logging.ERROR):
            result = main(["--load-model", str(tmp_path / "absent.joblib"), "--no-loop"])

        assert result == 1
        assert "Could not load model" in caplog.text

    def test_load_metrics_absent_sidecar_returns_empty(self, tmp_path: Path) -> None:
        assert load_metrics(tmp_path / "absent.joblib") == {}

    def test_cli_load_model_corrupt_sidecar_exits_nonzero(
        self, trained_report, tmp_path: Path
    ) -> None:
        pipeline, _ = trained_report
        model_path = tmp_path / "m.joblib"
        save_model(pipeline, model_path)
        metrics_path_for(model_path).write_text('{"accuracy": 1.0}', encoding="utf-8")

        assert main(["--load-model", str(model_path), "--no-loop"]) == 1

    def test_cli_load_model_ignores_missing_dataset(
        self, trained_report, tmp_path: Path
    ) -> None:
        pipeline, report = trained_report
        model_path = tmp_path / "m.joblib"
        save_model(pipeline, model_path, metrics=asdict(report))
        args = Namespace(
            load_model=str(model_path),
            data=str(tmp_path / "absent.csv"),
            test_size=TEST_SIZE,
            classifier="nb",
            save_model=None,
            no_loop=True,
        )

        assert run(args) == 0


class TestInteractiveLoop:
    @pytest.fixture()
    def loop_pipeline(self):
        df = fallback_dataframe()
        X_train, _, y_train, _ = split_data(df)
        return train(build_pipeline("nb"), X_train, y_train)

    @staticmethod
    def _scripted_input(monkeypatch: pytest.MonkeyPatch, inputs: list[str]) -> None:
        script = iter(inputs)

        def fake_input(_prompt: str = "") -> str:
            try:
                return next(script)
            except StopIteration:
                raise EOFError from None

        monkeypatch.setattr("builtins.input", fake_input)

    def test_loop_classifies_then_quits(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        self._scripted_input(
            monkeypatch,
            ["Win a free prize now!!!", "  Meeting at 10am tomorrow, see you there  ", "quit"],
        )

        assert _interactive_loop(loop_pipeline) is None

        out = capsys.readouterr().out
        assert "SPAM" in out
        assert "HAM" in out
        assert out.count("confidence") == 2
        assert "Goodbye." in out

    @pytest.mark.parametrize("command", ["quit", "exit", ":q", "QUIT", "  quit  "])
    def test_loop_exit_commands(
        self,
        loop_pipeline,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        command: str,
    ) -> None:
        self._scripted_input(monkeypatch, [command])

        assert _interactive_loop(loop_pipeline) is None

        out = capsys.readouterr().out
        assert "Goodbye." in out
        assert "confidence" not in out

    def test_loop_message_containing_exit_word_classifies(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        self._scripted_input(monkeypatch, ["please quit now", "quit"])

        assert _interactive_loop(loop_pipeline) is None

        out = capsys.readouterr().out
        assert out.count("confidence") == 1
        assert "Goodbye." in out

    def test_loop_keyboard_interrupt_exits_cleanly(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        def fake_input(_prompt: str = "") -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", fake_input)

        assert _interactive_loop(loop_pipeline) is None

        assert "Goodbye." in capsys.readouterr().out

    def test_loop_blank_input_reprompts(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        script = iter(["", "   ", "\t", "exit"])
        calls: list[str] = []

        def fake_input(_prompt: str = "") -> str:
            try:
                value = next(script)
            except StopIteration:
                raise EOFError from None
            calls.append(value)
            return value

        monkeypatch.setattr("builtins.input", fake_input)

        assert _interactive_loop(loop_pipeline) is None

        assert calls == ["", "   ", "\t", "exit"]
        out = capsys.readouterr().out
        assert "confidence" not in out
        assert "Goodbye." in out

    def test_loop_eof_exits_cleanly(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        self._scripted_input(monkeypatch, [])

        assert _interactive_loop(loop_pipeline) is None

        assert "Goodbye." in capsys.readouterr().out

    def test_loop_output_format(
        self, loop_pipeline, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        self._scripted_input(
            monkeypatch, ["Meeting at 10am tomorrow, see you there", "quit"]
        )

        _interactive_loop(loop_pipeline)

        out = capsys.readouterr().out
        assert re.search(r"  HAM \(\d+\.\d% confidence\)", out)

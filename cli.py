"""CLI for the SMS Spam Classifier: evaluation display + interactive loop (FR-B4..B7).

Flow: load dataset -> stratified split -> train -> evaluate/print -> loop.
"""
from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence
from pathlib import Path

from config import (
    CLASSIFIERS,
    DEFAULT_CLASSIFIER,
    DEFAULT_MODEL_PATH,
    TEST_SIZE,
)
from dataset import load_dataset, resolve_dataset_path, split_data
from evaluate import evaluate, format_report
from model import (
    build_pipeline,
    load_model,
    predict_with_confidence,
    save_model,
    train,
)

logger = logging.getLogger("spam-detector")

EXIT_COMMANDS = {"quit", "exit", ":q"}
LOOP_HELP = "type a message to classify · 'quit' / 'exit' / ':q' to leave"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spam-detector",
        description=(
            "SMS spam classifier (TF-IDF + MultinomialNB) with metrics and an "
            "interactive prediction loop."
        ),
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help=(
            "path to a labelled dataset (CSV/TSV, label+text columns). "
            "Default: data/sms_spam_collection.csv if present, else the "
            "built-in fallback dataset"
        ),
    )
    parser.add_argument(
        "--classifier",
        choices=CLASSIFIERS,
        default=DEFAULT_CLASSIFIER,
        help="nb = MultinomialNB (default), lr = LogisticRegression",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=TEST_SIZE,
        help="stratified test fraction (default: %(default)s)",
    )
    parser.add_argument(
        "--load-model",
        type=str,
        default=None,
        metavar="PATH",
        help="skip training and load a saved model",
    )
    parser.add_argument(
        "--save-model",
        nargs="?",
        const=str(DEFAULT_MODEL_PATH),
        default=None,
        metavar="PATH",
        help=f"save the trained model (default path: {DEFAULT_MODEL_PATH})",
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="evaluate and exit without the interactive prompt (for scripts/QA)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    return parser


def _interactive_loop(pipeline) -> None:
    """FR-B6: read messages from stdin until quit/exit/:q/EOF/Ctrl+C."""
    print(f"\nInteractive mode — {LOOP_HELP}")
    while True:
        try:
            text = input("\nsms> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return
        if not text:
            continue
        if text.lower() in EXIT_COMMANDS:
            print("Goodbye.")
            return
        label, confidence = predict_with_confidence(pipeline, text)
        print(f"  {label} ({confidence:.1f}% confidence)")


def run(args: argparse.Namespace) -> int:
    if args.load_model:
        try:
            pipeline = load_model(args.load_model)
        except Exception as exc:
            raise ValueError(f"Could not load model from {args.load_model}: {exc}") from exc
        print(f"Loaded model from {args.load_model} (evaluation skipped).")
    else:
        source = resolve_dataset_path(args.data)  # raises if explicit path is missing
        df = load_dataset(source)

        if source is None:
            print("=" * 64)
            print(
                f"WARNING: running on the built-in DEMO dataset ({len(df)} labelled rows)."
            )
            print("Metrics are illustrative only — pass the real SMS Spam")
            print("Collection file via --data for benchmark-quality results.")
            print("=" * 64)
        else:
            print(f"Dataset: {source} ({len(df)} rows)")

        X_train, X_test, y_train, y_test = split_data(df, test_size=args.test_size)
        pipeline = train(build_pipeline(args.classifier), X_train, y_train)
        report = evaluate(pipeline, X_test, y_test)

        print(f"Classifier: {args.classifier} | train: {len(X_train)} | test: {len(X_test)}")
        print()
        print(format_report(report))

        if args.save_model:
            saved = save_model(pipeline, Path(args.save_model))
            print(f"\nModel saved to {saved}")

    if args.no_loop:
        return 0
    _interactive_loop(pipeline)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        return run(args)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1
    except ValueError as exc:
        logger.error("%s", exc)
        return 1
    except OSError as exc:
        logger.error("Filesystem error: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

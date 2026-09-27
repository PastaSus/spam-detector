"""Dataset loading for the SMS Spam Classifier (FR-B2, FR-B3).

Resolution order:
1. explicit path passed by the caller / ``--data``
2. ``data/sms_spam_collection.csv`` (the UCI SMS Spam Collection, if present)
3. built-in fallback dataset of labelled tuples — ``1 = spam``, ``0 = ham`` —
   covering the lab sheet's spam families (prize claims, urgent account
   notices, work-from-home offers, free vacation claims) and ham families
   (meeting reminders, project updates, casual conversation).

Everything is normalized into a Pandas DataFrame with columns ``text`` and
``label`` (int).
"""
from __future__ import annotations

import logging
import math
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from config import HAM, RANDOM_STATE, SPAM, SMS_SPAM_COLLECTION_PATH, TEST_SIZE

logger = logging.getLogger(__name__)

# --- Built-in fallback dataset (lab reference tuples) ------------------------
FALLBACK_DATASET: list[tuple[str, int]] = [
    # --- spam: prize claims ---
    ("Congratulations! You've won a $1000 prize. Click here to claim it now!", SPAM),
    ("You have been selected to win a cash prize. Send your details to claim.", SPAM),
    ("WINNER! Claim your $500 shopping voucher before it expires today.", SPAM),
    # --- spam: urgent account notices ---
    ("URGENT: Your account will be suspended. Verify your password immediately.", SPAM),
    ("Security alert: unusual login detected. Confirm your identity at once.", SPAM),
    ("Final notice: your card will be blocked. Update your details NOW.", SPAM),
    # --- spam: work-from-home offers ---
    ("Earn $5000 per week working from home. No experience needed. Reply START.", SPAM),
    ("Work 2 hours a day from home and make money fast. Limited spots left!", SPAM),
    ("Part-time remote job offering $30/hour. Click the link to apply today.", SPAM),
    # --- spam: free vacation claims ---
    ("Free vacation! You've earned a free trip to Bali. Call now to redeem.", SPAM),
    ("Claim your free holiday package before the offer expires. Tap here!", SPAM),
    ("You're getting a free weekend getaway — confirm your travel dates now.", SPAM),
    # --- ham: meeting reminders ---
    ("Hey, are we still meeting for coffee at 10am tomorrow?", HAM),
    ("Reminder: project standup starts at 9:30 in room 204.", HAM),
    ("Running 10 minutes late for the meeting, please start without me.", HAM),
    # --- ham: project updates ---
    ("The team updated sections 2 and 3 of the report — can you review them?", HAM),
    ("Lab notes are uploaded to the class drive. Let me know if the link breaks.", HAM),
    ("Sprint done: 14 of 16 tickets closed. Retro moved to Thursday.", HAM),
    # --- ham: casual conversation ---
    ("Mom called, dinner at grandma's on Sunday at 6pm.", HAM),
    ("Can you pick up milk and bread on your way home?", HAM),
    ("Movie night still on tonight? Let me know what time to meet.", HAM),
    ("Thanks for your help today, really appreciate it!", HAM),
    ("Happy birthday! Hope you have an amazing day :)", HAM),
]

LABEL_MAP: dict[str, int] = {
    "spam": SPAM,
    "ham": HAM,
    str(SPAM): SPAM,
    str(HAM): HAM,
}


def normalize_label(raw: object) -> int | None:
    """Map ``spam``/``ham``/``1``/``0`` (any case/whitespace) to int; None if unknown."""
    if raw is None:
        return None
    key = str(raw).strip().lower()
    if not key or key == "nan":
        return None
    return LABEL_MAP.get(key)


def fallback_dataframe() -> pd.DataFrame:
    """Built-in labelled dataset as a DataFrame (FR-B2 fallback)."""
    frame = pd.DataFrame(FALLBACK_DATASET, columns=["text", "label"])
    frame["label"] = frame["label"].astype(int)
    return frame


def resolve_dataset_path(explicit: Path | str | None = None) -> Path | None:
    """Return the dataset file to use, or None when the fallback applies.

    Raises FileNotFoundError when an explicit path does not exist (fail loudly
    for user-specified input instead of silently substituting data — NFR-B2).
    """
    if explicit is not None:
        path = Path(explicit)
        if not path.is_file():
            raise FileNotFoundError(f"Dataset file not found: {path}")
        return path
    if SMS_SPAM_COLLECTION_PATH.is_file():
        return SMS_SPAM_COLLECTION_PATH
    return None


def _normalize_frame(raw: pd.DataFrame, source: Path) -> pd.DataFrame:
    if raw.shape[1] < 2:
        raise ValueError(
            f"Dataset {source} must have at least 2 columns (label, text); "
            f"found {raw.shape[1]}"
        )

    frame = raw.iloc[:, :2].copy()
    frame.columns = ["raw_label", "raw_text"]
    frame["text"] = frame["raw_text"].astype(str).str.strip()
    frame["label"] = frame["raw_label"].map(normalize_label)

    dropped = int(frame["label"].isna().sum())
    frame = frame.dropna(subset=["label"])
    frame = frame[frame["text"].str.len() > 0]
    if frame.empty:
        raise ValueError(f"Dataset {source} contains no usable labelled rows.")
    frame["label"] = frame["label"].astype(int)

    if dropped:
        # Common when the file starts with a header row (label,text / v1,v2).
        logger.warning("Dropped %d row(s) with unrecognized labels from %s", dropped, source)
    if frame["label"].nunique() < 2:
        logger.warning("Only one class present in %s — stratified split will fail.", source)

    return frame[["text", "label"]].reset_index(drop=True)


def _read_labeled_file(path: Path) -> pd.DataFrame:
    separator = "\t" if path.suffix.lower() in {".tsv", ".tab"} else ","
    try:
        raw = pd.read_csv(path, sep=separator, header=None, dtype=str, on_bad_lines="skip")
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse dataset file {path}: {exc}") from exc
    return _normalize_frame(raw, source=path)


def load_dataset(csv_path: Path | str | None = None) -> pd.DataFrame:
    """Load labelled data into a Pandas DataFrame with ``text`` + int ``label``.

    ``csv_path=None`` triggers automatic resolution (default file or fallback).
    """
    source = resolve_dataset_path(csv_path)
    if source is None:
        logger.warning(
            "No dataset file found (looked for %s) — using built-in fallback "
            "dataset (%d rows).",
            SMS_SPAM_COLLECTION_PATH,
            len(FALLBACK_DATASET),
        )
        return fallback_dataframe()
    return _read_labeled_file(source)


def split_data(
    df: pd.DataFrame,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    """Stratified train/test split (FR-B3, AD-B4). Returns X_train, X_test, y_train, y_test."""
    if len(df) < 4:
        raise ValueError(f"Need at least 4 rows to split; got {len(df)}.")
    if df["label"].nunique() < 2:
        raise ValueError(
            "Stratified split needs at least 2 classes (spam and ham); "
            f"got labels {sorted(df['label'].unique().tolist())}."
        )
    class_counts = df["label"].value_counts()
    if class_counts.min() < 2:
        raise ValueError(
            "Stratified split needs at least 2 rows per class; got "
            f"{class_counts.to_dict()}."
        )
    n_classes = int(df["label"].nunique())
    if isinstance(test_size, float):
        test_rows = math.ceil(len(df) * test_size)
    else:
        test_rows = int(test_size)
    if test_rows < n_classes:
        raise ValueError(
            "Test split would hold fewer rows than classes "
            f"({test_rows} < {n_classes}); increase test_size so every class "
            "appears in the test set."
        )
    return train_test_split(
        df["text"],
        df["label"],
        test_size=test_size,
        random_state=random_state,
        stratify=df["label"],
    )

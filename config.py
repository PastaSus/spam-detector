"""Central configuration for the SMS Spam Classifier.

Mirrors the lab reference sheet: TfidfVectorizer(lowercase=True,
stop_words="english") paired with MultinomialNB (Logistic Regression offered
as the lab's permitted alternative).
"""
from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# --- Dataset resolution (FR-B2) ---------------------------------------------
# Priority: explicit --data path > SMS Spam Collection file (if present) > built-in fallback.
SMS_SPAM_COLLECTION_PATH = DATA_DIR / "sms_spam_collection.csv"  # user-supplied UCI file
DEMO_CSV_PATH = DATA_DIR / "sample_sms.csv"  # shipped demo file (--data data/sample_sms.csv)

# --- Splitting (FR-B3, NFR-B1) ----------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.2

# --- Model (FR-B1) ----------------------------------------------------------
TFIDF_PARAMS: dict[str, object] = {"lowercase": True, "stop_words": "english"}
CLASSIFIERS: tuple[str, ...] = ("nb", "lr")  # nb = MultinomialNB (default), lr = LogisticRegression
DEFAULT_CLASSIFIER = "nb"

# --- Persistence (FR-B7) ----------------------------------------------------
MODELS_DIR = BASE_DIR / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "spam-model.joblib"

# --- Label contract (AD-B1) -------------------------------------------------
SPAM = 1
HAM = 0

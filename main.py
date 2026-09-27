"""Entry point for the SMS Spam Classifier.

Usage:
    python main.py                      # built-in fallback dataset + interactive loop
    python main.py --data data/sample_sms.csv
    python main.py --no-loop            # metrics only (scripting / QA)
"""
from __future__ import annotations

import sys

from cli import main

if __name__ == "__main__":
    sys.exit(main())

# `spam-detector` datasets

## Resolution order (FR-B2)

1. **Explicit path** — `python main.py --data path/to/file.csv` (must exist, otherwise the CLI errors).
2. **`data/sms_spam_collection.csv`** — the real UCI *SMS Spam Collection* file, if you place it here.
3. **Built-in fallback** — 23 labelled tuples shipped inside `dataset.py` (used automatically; the CLI prints a DEMO-dataset warning).

## Accepted formats

- `.csv` (comma) and `.tsv` (tab) separators
- Two columns in either order of importance: **label + text**
  - label values: `spam` / `ham` / `1` / `0` (case-insensitive)
- Header rows (`label,text` or `v1,v2`) are detected and dropped automatically
- Extra columns beyond the first two are ignored

## Getting the real SMS Spam Collection (UCI)

Download `SMSSpamCollection` from the UCI ML Repository and save it next to this
README as `sms_spam_collection.csv` (it is tab-separated and has no header —
the loader handles both):

```bash
# from the spam-detector/ folder
python main.py --data data/sms_spam_collection.csv
```

## Shipped demo file

`sample_sms.csv` — 10 rows (5 spam / 5 ham) for quick demos:

```bash
python main.py --data data/sample_sms.csv
```

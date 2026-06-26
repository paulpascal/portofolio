"""
Stage 01 - Data collection / ingestion.

Lifecycle: collection, ingestion
Architecture: batch ingestion of semi-structured form data

Reads the raw monthly form submissions (one nested JSON object per line, the kind
ODK / KoboToolbox produce) and flattens them into a tidy long table that the rest
of the pipeline can consume. It does NOT clean or validate yet, that is stage 02,
on purpose: ingestion should faithfully land what was submitted.

Run (after ../_shared/generate_data.py):
    python ingest.py
Output:
    ../_shared/data/indicators_long.csv
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "_shared" / "data"
SRC = SHARED / "submissions.jsonl"
OUT = SHARED / "indicators_long.csv"

rows = []
n_files = 0
with open(SRC) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        n_files += 1
        metrics = rec.get("metrics", {}) or {}
        for indicator, value in metrics.items():
            rows.append({
                "submission_at": rec.get("submitted_at"),
                "site_id": rec.get("site_id"),
                "country_raw": rec.get("country"),
                "period": rec.get("period"),
                "indicator": indicator,
                "value_raw": "" if value is None else value,
                "target_households": rec.get("target_households"),
                "reported_by": rec.get("reported_by"),
            })

OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Ingested {n_files} submissions -> {len(rows)} indicator rows")
print(f"Wrote {OUT.relative_to(ROOT)}")

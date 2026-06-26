"""
Stage 02 - Cleaning and data quality.

Lifecycle: cleaning, data quality, validation
Architecture: pandas transformation + a small assertion-based quality suite
              (the same idea as Great Expectations / dbt tests, kept lightweight)

Takes the ingested long table, cleans it reproducibly, then runs explicit quality
checks and writes both a curated dataset and a machine-readable quality report.
Bad values are flagged and quarantined, never silently dropped.

Run (after 01-data-collection/ingest.py):
    python clean_and_check.py
Outputs:
    ../_shared/data/curated/indicators.parquet
    ../_shared/data/curated/quarantine.csv
    quality_report.json   (next to this script)
"""
import json
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd


def normalize_label(x):
    s = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode()
    return s.strip().title()

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "_shared" / "data"
CUR = SHARED / "curated"
CUR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(SHARED / "indicators_long.csv")
sites = pd.read_csv(SHARED / "sites.csv")
n_raw = len(df)

# ---- clean ------------------------------------------------------------------
df["country"] = df["country_raw"].map(normalize_label)


def to_num(x):
    s = str(x).strip().replace(",", "")
    if s in ("", "nan", "None"):
        return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan


df["value"] = df["value_raw"].map(to_num)

dups = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

# valid site reference?
valid_sites = set(sites["site_id"])
df["site_known"] = df["site_id"].isin(valid_sites)

# ---- quality checks (assertion suite) --------------------------------------
checks = []


def check(name, mask_bad, severity="error"):
    """mask_bad: boolean Series, True where the row FAILS the check."""
    n_bad = int(mask_bad.sum())
    checks.append({"check": name, "severity": severity,
                   "failed_rows": n_bad, "passed": n_bad == 0})
    return mask_bad


bad_missing = check("value_not_null", df["value"].isna())
bad_negative = check("value_non_negative", df["value"] < 0)
bad_type = check("value_is_numeric", df["value_raw"].astype(str).str.strip().ne("")
                 & df["value"].isna())
bad_site = check("site_id_in_reference", ~df["site_known"])
# per-indicator outliers (IQR), informational
def iqr_out(s):
    q1, q3 = s.quantile([.25, .75])
    return s > q3 + 3 * (q3 - q1)
out_mask = df.groupby("indicator")["value"].transform(iqr_out).fillna(False)
bad_outlier = check("value_within_iqr_fence", out_mask, severity="warning")
# uniqueness of grain
grain_dup = df.duplicated(subset=["site_id", "period", "indicator"], keep=False)
check("unique_site_period_indicator", grain_dup & df["value"].notna(), severity="warning")

# extreme outliers are flagged AND quarantined: kept for review, kept out of the
# analytical layer so they cannot distort marts, dashboards or the model.
bad = bad_missing | bad_negative | bad_type | bad_site | bad_outlier
quarantine = df[bad].copy()
curated = df[~bad].copy()
curated = curated[["site_id", "country", "period", "indicator", "value",
                   "target_households", "reported_by"]]

curated.to_parquet(CUR / "indicators.parquet", index=False)
quarantine.to_csv(CUR / "quarantine.csv", index=False)

report = {
    "source_rows": n_raw,
    "duplicate_rows_removed": dups,
    "curated_rows": int(len(curated)),
    "quarantined_rows": int(len(quarantine)),
    "completeness_pct": round(100 * curated["value"].notna().mean(), 1),
    "country_labels_before": int(df["country_raw"].nunique()),
    "country_labels_after": int(curated["country"].nunique()),
    "outliers_flagged": int(out_mask.sum()),
    "checks": checks,
    "note": "synthetic data",
}
with open(Path(__file__).resolve().parent / "quality_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps({k: report[k] for k in
                  ["source_rows", "duplicate_rows_removed", "curated_rows",
                   "quarantined_rows", "country_labels_before",
                   "country_labels_after", "outliers_flagged"]}, indent=2))
print("Checks:")
for c in checks:
    flag = "PASS" if c["passed"] else f"{c['severity'].upper()} ({c['failed_rows']})"
    print(f"  [{flag}] {c['check']}")

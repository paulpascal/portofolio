# 02 · Cleaning & data quality

**Lifecycle:** cleaning · validation · data quality  **Architecture:** pandas + an assertion-based
quality suite (same idea as Great Expectations / dbt tests, kept lightweight)

Cleans the ingested data reproducibly (normalises country labels including accents, coerces types,
drops duplicates) then runs explicit checks: not-null, non-negative, numeric, referential integrity
to the site reference, grain uniqueness, and IQR outlier fences. Bad and extreme rows are
**quarantined**, never silently dropped, and a machine-readable `quality_report.json` records every check.

```bash
python clean_and_check.py    # -> ../_shared/data/curated/indicators.parquet + quarantine.csv + quality_report.json
```

Sample run: 72 duplicates removed, 30 raw country spellings normalised to 10, ~200 rows quarantined
across the checks. Synthetic data only.

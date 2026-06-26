# 03 · Transformations & marts

**Lifecycle:** transformation · modelling · marts  **Architecture:** analytics engineering on a local
warehouse (DuckDB + SQL), staging to fact to mart (the layering you would use in dbt)

Builds a small star-style model from the curated data:

- `stg_indicators`: long data pivoted to one row per site/period
- `fact_site_month`: adds site dimensions, target attainment and a below-target flag
- `mart_country_month`: country × month roll-up for BI and reporting

```bash
python build_marts.py    # -> ../_shared/data/marts/{fact_site_month,mart_country_month}.parquet
```

Synthetic data only.

# 01 · Data collection / ingestion

**Lifecycle:** collection · ingestion  **Architecture:** batch ingestion of semi-structured form data

Flattens nested monthly form submissions (one JSON object per line, the shape ODK / KoboToolbox
produce) into a tidy long table. Ingestion lands data faithfully; cleaning happens in stage 02.

```bash
python ../_shared/generate_data.py   # once, creates the synthetic source
python ingest.py                      # -> ../_shared/data/indicators_long.csv
```

Synthetic data only.

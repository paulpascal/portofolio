# 04 · Large-scale analytics

**Lifecycle:** processing · aggregation at scale  **Architecture:** columnar, partitioned Parquet
queried with DuckDB (out-of-core); the same query for Spark is in `spark_reference.py`

Generates a few million synthetic visit events, writes them as Parquet **partitioned by country**, and
runs a partition-aware aggregation, timing it. Demonstrates the big-data pattern, columnar storage plus
partition pruning plus an engine that does not load everything into memory, at laptop scale.

```bash
python run.py            # ~3M rows (aggregates in well under a second)
python run.py 8000000    # push the row count higher
```

`spark_reference.py` shows the distributed-engine version (run with `spark-submit` on a cluster; not
part of the local demo). Synthetic data only. The generated `events_parquet/` is git-ignored.

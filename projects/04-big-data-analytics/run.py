"""
Stage 04 - Large-scale analytics.

Lifecycle: processing, aggregation at scale
Architecture: columnar, partitioned Parquet queried with DuckDB (out-of-core).
              The same query expressed for Spark is in spark_reference.py.

Generates a few million synthetic visit-level events, writes them as Parquet
partitioned by country, and runs a partition-aware aggregation, timing it. This
shows the "big data" pattern (columnar storage + partition pruning + engine that
does not load everything into memory) on a laptop-friendly scale.

Run:
    python run.py            # ~3M rows by default
    python run.py 8000000    # bump the row count
"""
import sys
import time
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import duckdb

HERE = Path(__file__).resolve().parent
LAKE = HERE / "events_parquet"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3_000_000
COUNTRIES = ["Togo", "Benin", "Mali", "Senegal", "Cote d'Ivoire",
             "Uganda", "Kenya", "Rwanda", "Ghana", "Niger"]


def generate():
    rng = np.random.default_rng(11)
    print(f"Generating {N:,} synthetic visit events ...")
    country_idx = rng.integers(0, len(COUNTRIES), N)
    months = rng.integers(1, 13, N)
    table = pa.table({
        "country": pa.array([COUNTRIES[i] for i in country_idx]),
        "month": pa.array(months),
        "households": pa.array(rng.integers(1, 6, N)),
        "children": pa.array(rng.integers(0, 9, N)),
        "referred": pa.array(rng.integers(0, 2, N)),
    })
    pq.write_to_dataset(table, root_path=str(LAKE), partition_cols=["country"])
    size = sum(f.stat().st_size for f in LAKE.rglob("*.parquet")) / 1e6
    print(f"Wrote partitioned Parquet to {LAKE.name}/ ({size:.1f} MB on disk)")


def aggregate():
    con = duckdb.connect()
    q = f"""
        SELECT country,
               COUNT(*)            AS events,
               SUM(households)     AS households,
               SUM(children)       AS children_screened,
               ROUND(AVG(referred), 3) AS referral_rate
        FROM read_parquet('{LAKE}/**/*.parquet', hive_partitioning=1)
        GROUP BY country
        ORDER BY events DESC
    """
    t0 = time.perf_counter()
    df = con.execute(q).df()
    dt = time.perf_counter() - t0
    total = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{LAKE}/**/*.parquet', hive_partitioning=1)"
    ).fetchone()[0]
    print(f"\nAggregated {total:,} rows in {dt:.2f}s with DuckDB:")
    print(df.to_string(index=False))

    # partition pruning: scanning ONE country touches far less data
    t0 = time.perf_counter()
    one = con.execute(
        f"""SELECT COUNT(*) FROM read_parquet('{LAKE}/**/*.parquet', hive_partitioning=1)
            WHERE country = 'Togo'"""
    ).fetchone()[0]
    print(f"\nPartition-pruned scan (Togo only): {one:,} rows in "
          f"{time.perf_counter()-t0:.2f}s (reads just the Togo partition).")


if __name__ == "__main__":
    if not LAKE.exists():
        generate()
    else:
        print(f"Using existing {LAKE.name}/ (delete it to regenerate).")
    aggregate()

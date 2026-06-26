"""
Reference only - the same large-scale aggregation expressed in PySpark.

This is the distributed-engine version of the DuckDB query in run.py. It is here to
show the architecture; it is not run as part of the demo (it needs a Spark runtime).
On a cluster you would point `path` at object storage (S3/GCS/ADLS) instead of a
local folder, and Spark would parallelise the scan across executors.

    spark-submit spark_reference.py
"""
from pyspark.sql import SparkSession, functions as F


def main():
    spark = (SparkSession.builder
             .appName("visit-events-aggregation")
             .getOrCreate())

    # Partitioned Parquet, same layout as run.py writes (country=<...>/...)
    events = spark.read.parquet("events_parquet")

    by_country = (events
                  .groupBy("country")
                  .agg(F.count("*").alias("events"),
                       F.sum("households").alias("households"),
                       F.sum("children").alias("children_screened"),
                       F.round(F.avg("referred"), 3).alias("referral_rate"))
                  .orderBy(F.desc("events")))

    by_country.show(truncate=False)

    # Spark prunes partitions for a filtered country just like DuckDB does:
    events.filter(F.col("country") == "Togo").count()

    spark.stop()


if __name__ == "__main__":
    main()

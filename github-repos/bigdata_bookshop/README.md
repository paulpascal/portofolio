# Big Data Bookshop

Large-scale analytics over book-sales data: the big-data counterpart to my warehouse-based
[Bookshop ELT Pipeline](https://github.com/paulpascal/bookshop_project). Where that project models
sales in a warehouse with dbt, this one processes the data at scale with a distributed engine and
columnar storage.

> Note to self (remove before publishing): confirm and adjust the exact stack below to match the repo
> (distributed engine, storage format, and how jobs are run). The framing and structure are ready; just
> drop in the specifics.

## What it does

- Ingests and processes book-sales data at volume.
- Runs distributed transformations and aggregations (sales by title, author, region and period).
- Writes results to columnar storage for fast downstream querying and reporting.

## Stack

| Concern | Technology |
|--------|------------|
| Processing | distributed engine (Spark / PySpark) |
| Storage | columnar files (Parquet) / HDFS or object storage |
| Packaging | Docker |
| Language | Python |

## Run

```bash
# build and start the environment
docker-compose up --build

# submit the processing job (adjust to the repo's entry point)
spark-submit jobs/<job>.py
```

## What it demonstrates

Working with data at scale: distributed processing, partitioned columnar storage, and aggregation jobs
that stay fast as data grows, complementing the warehouse/dbt approach in the companion bookshop project.

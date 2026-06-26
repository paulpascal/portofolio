# Bookshop ELT Pipeline

A modern, containerised ELT platform for book-sales analytics: data is loaded into Snowflake and
transformed with dbt through layered models, orchestrated by Airflow, and served through a Streamlit
dashboard. It is a compact but complete example of how I build analytics pipelines: load raw first,
transform in the warehouse, test as you go, and keep every step reproducible in Docker.

## Architecture

| Concern | Choice |
|--------|--------|
| Source | PostgreSQL (operational book-sales data) |
| Warehouse | Snowflake |
| Transformation | dbt, layered RAW to STAGING to WAREHOUSE to MARTS |
| Orchestration | Airflow (each transform runs in an isolated dbt container via the DockerOperator) |
| Visualisation | Streamlit dashboard |
| Packaging | Docker Compose |

## Pipeline

1. **Init** (`init_snowflake` DAG) creates the Snowflake structure (databases, schemas, roles).
2. **Ingestion** (`ingestion` DAG) loads source data into the Snowflake `RAW` schema.
3. **Transformation** (`bookshop_data_transform_dag`) moves data through the dbt layers, each step in its
   own container for isolation and reproducibility:
   - RAW to STAGING (typing, renaming, light cleaning)
   - STAGING to WAREHOUSE (business logic, conformed dimensions and facts)
   - WAREHOUSE to MARTS (reporting tables)
4. **Visualisation**: the Streamlit dashboard reads the marts (KPIs, sales trends, customer segmentation,
   product analysis).

## Run

```bash
cp env_example .env        # set your Snowflake account + password
docker-compose up --build  # Postgres, Airflow (8080), dbt image, Streamlit (8501)
```

Then enable and trigger the DAGs in Airflow (`http://localhost:8080`) in the order above, and open the
dashboard at `http://localhost:8501`.

## Project layout

```
airflow/dags/      workflow definitions
data/init/         table creation and seed scripts
dbt_pipeline/      dbt models (staging, warehouse, marts) + project config
ingestion/         load scripts (RAW)
snowflake_config/  Snowflake initialisation
visualization/     Streamlit app
docker-compose.yml
```

## What it demonstrates

End-to-end ELT, layered dbt modelling, container-isolated transformations, workflow orchestration, and a
working BI layer, all reproducible from a single `docker-compose up`.

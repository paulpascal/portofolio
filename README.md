# Paul Alognon-Anani: portfolio

Personal site plus a set of small, runnable data projects. Data and software engineer in Lomé, Togo,
focused on data quality, pipelines, marts and dashboards for national-scale digital health.

- `index.html`: the personal site, a filterable grid of projects (no build step).
- `projects/`: six connected demos that walk the whole data lifecycle. All run on
  **synthetic data only**.

## The pipeline

The numbered projects form one connected flow, and each also runs on its own:

| # | Project | Lifecycle | Architecture |
|---|---------|-----------|--------------|
| 01 | Data collection / ingestion | collection, ingestion | batch ingestion of semi-structured forms |
| 02 | Cleaning & data quality | cleaning, validation, quality | pandas + assertion-based checks |
| 03 | Transformations & marts | transformation, marts | DuckDB + SQL (staging to fact to mart) |
| 04 | Large-scale analytics | processing at scale | partitioned Parquet + DuckDB (Spark reference included) |
| 05 | Prediction | machine learning | scikit-learn on the marts |
| 06 | BI dashboard | dashboards, reporting | static Chart.js page reading the marts |
| 07 | Production health-data platform | full lifecycle, ~100k users | CouchDB/ODK/Kobo ingestion, dbt, FastAPI, Docker, Kubernetes, Flutter app |

## Run the whole pipeline

```bash
pip install pandas numpy duckdb scikit-learn pyarrow
python projects/_shared/generate_data.py
python projects/01-data-collection/ingest.py
python projects/02-cleaning-quality/clean_and_check.py
python projects/03-transformations-marts/build_marts.py
python projects/04-big-data-analytics/run.py
python projects/05-prediction/train.py
python projects/06-bi-dashboard/build_dashboard_data.py
```

Then open `projects/06-bi-dashboard/index.html`.

Project 07 (the flagship platform) has its own stack; see `projects/07-production-health-platform/README.md`.

## Existing GitHub repos

`github-repos/` holds rewritten, portfolio-grade READMEs for my other public projects (bookshop ELT
pipeline, big-data bookshop, ML model manager, MongoDB sharded cluster). See `github-repos/NOTES.md` for
how to drop them into each repo.

## Publish on GitHub Pages

1. Create a public repo named `portofolio` under `github.com/paulpascal`.
2. `git init && git add . && git commit -m "Portfolio site and data pipeline demos" && git branch -M main`
   then `git remote add origin https://github.com/paulpascal/portofolio.git && git push -u origin main`.
3. In Settings, open Pages, choose "Deploy from a branch", and pick `main` / `/ (root)`.
4. Site: `https://paulpascal.github.io/portofolio/`.
   Dashboard: `.../portofolio/projects/06-bi-dashboard/index.html`.

If you name the repo differently, change the `REPO` constant near the top of the `<script>` in
`index.html` so the "code" links resolve.

## Before you publish

- The Contact section in `index.html` already points to paul.alogno@gmail.com and github.com/paulpascal.
- No real or confidential data lives here. The demos are synthetic by design; generated data and the
  large Parquet folder are git-ignored and rebuilt by the scripts.

---

*Built by hand. Demo data is synthetic.*

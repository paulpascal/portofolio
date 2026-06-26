# How to use these READMEs

Each folder here holds a rewritten, portfolio-grade `README.md` for one of your existing GitHub repos.
I cannot push to your GitHub, so the steps are yours to run. For each repo: replace its `README.md` with
the one here, commit, and push.

## Per repo

- **bookshop_project** to drop in `bookshop_project/README.md`. Clean already; the new one is tightened
  and adds a short "what it demonstrates" framing. Optionally set the repo description to
  "Modern ELT pipeline: Snowflake, Airflow, dbt, Streamlit, Docker".

- **versioning_ml_web_app** to drop in `versioning_ml_web_app/README.md`. This removes the class framing
  (the contributors table and "Spécifications du Projet / Objectifs / Fonctionnalités Requises" sections)
  and translates it to English. Set the repo description to "ML model-training web app with DVC
  versioning and Jenkins CI".

- **group9_nosql** to this one needs a rename to shed the "group 9 / devoir" look:
  1. Rename the repo to `mongodb-sharded-cluster` (Settings to Rename).
  2. Replace `README.md` with `mongodb-sharded-cluster/README.md` (English, no "Groupe9 / Devoir").
  3. Remove or rename `MongoDB_Devoir.png` (for example to `sharding-topology.png`) and update the image
     link if you keep it; consider removing `notes.md` if it is class notes.
  4. Set the repo description to "Sharded MongoDB cluster with Docker Compose: replication and horizontal
     scaling".

- **bigdata_bookshop** to drop in `bigdata_bookshop/README.md`, but first confirm the stack: I could not
  open this repo to read it, so I left a short "note to self" block and generic stack rows. Adjust the
  engine/storage/run command to match the actual code, then delete that note block.

## General cleanup that makes repos read as portfolio work, not coursework

- Remove contributor/team tables and any "assignment / devoir / groupe" wording.
- Add a one-line repo **description** and a few **topics** on GitHub (e.g. dbt, airflow, snowflake, spark,
  mongodb, mlops).
- Make sure each README opens with what the project does and why, not setup steps.
- Add an MIT `LICENSE` if you want them to read as open-source.

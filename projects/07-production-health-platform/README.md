# 07 · Community health-data platform (reference implementation)

**Lifecycle:** collection to ingestion to staging to intermediate to marts to dashboards (with data quality at every layer)
**Architecture:** event-sourced collection (CouchDB / ODK / Kobo) to async ingestion workers to warehouse to dbt to BI + mobile, containerised with Docker and deployed on Kubernetes.

This is the flagship reference project: an end-to-end platform for a community-health programme sized
for roughly **100,000 active users** (community health workers and supervisors submitting from the field),
built the way I would build it in production. It is a reference implementation, so some components expect
external services (a CouchDB cluster, a Kobo/ODK server, a warehouse); the code, models, manifests and
mobile app are all real and readable.

## What it does

1. **Collection**: a mobile app (Flutter) lets community health workers submit forms offline; data syncs
   to **CouchDB** when a connection is available. The platform can also pull from **ODK Central** and
   **KoboToolbox** for programmes that already use them.
2. **Ingestion**: stateless workers tail the CouchDB `_changes` feed (and poll the ODK/Kobo APIs),
   land raw documents immutably, and stream them into the warehouse `raw` schema. Workers are idempotent
   and resumable (they checkpoint the change sequence).
3. **Transformation**: a **dbt** project models the data in layers: `staging` (typed, renamed, lightly
   cleaned), `intermediate` (business logic, joins, enrichment), `marts` (fact and dimension tables and
   reporting roll-ups). Every layer carries **tests** (not-null, accepted values, relationships,
   freshness), which is where data quality is enforced.
4. **Serving**: a **FastAPI** service reads the marts (with a Redis cache) and serves a BI dashboard and
   the mobile app's read views.
5. **Operations**: everything is containerised (Docker) and deployed on **Kubernetes** with horizontal
   autoscaling, resource limits, scheduled dbt runs (CronJob), config and secrets, and an ingress.

## Architecture at a glance

```
 Collection      Flutter app, ODK Central, KoboToolbox
 Ingestion       stateless workers tail CouchDB _changes (idempotent, checkpointed)
 Warehouse raw   immutable landing of every source document
 dbt             staging, then intermediate, then marts  (tests = data quality)
 Serving         FastAPI + Redis
 Consumers       BI dashboard and mobile read views
```

See [`docs/architecture.md`](docs/architecture.md) for the scaling design (how it holds 100k users),
capacity assumptions, and failure handling.

## Repository layout

```
ingestion/      CouchDB _changes consumer + ODK/Kobo pullers (Python), Dockerised
transform/      dbt project: models/{staging,intermediate,marts} + tests
quality/        data-quality strategy and standalone checks
api/            FastAPI service serving marts to the dashboard and mobile app
dashboard/      static BI dashboard (Chart.js) backed by the API
mobile/         Flutter app (offline-first form capture + dashboards)
deploy/k8s/     Kubernetes manifests (deployments, services, HPA, CronJob, ingress, config, secrets)
docs/           architecture and scaling notes
docker-compose.yml   local stack for development
```

## Run locally

```bash
cp .env.example .env
docker compose up --build        # CouchDB, Postgres warehouse, ingestion, API, dashboard
# then run the models:
docker compose run --rm dbt dbt build      # staging -> intermediate -> marts + tests
```

Dashboard: <http://localhost:8080>. API docs: <http://localhost:8000/docs>. CouchDB: <http://localhost:5984/_utils>.

## Deploy on Kubernetes

```bash
kubectl apply -f deploy/k8s/
```

Manifests include the API (autoscaled), the ingestion worker, a dbt CronJob, services, an ingress, and
config/secret templates. See [`deploy/k8s/README.md`](deploy/k8s/README.md).

---

*Reference implementation. Any sample data is synthetic. No real or confidential data is included.*

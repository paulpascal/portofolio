# Architecture and scaling

## Goals

- Support roughly **100,000 active field users** (community health workers and supervisors) who submit
  forms, often offline, from low-connectivity areas.
- Keep collection reliable and offline-first, keep analytics trustworthy, and keep the whole thing
  operable by a small team.

## Design principles

1. **Offline-first collection.** The phone is the source of truth at the edge. The Flutter app stores
   submissions locally and syncs to CouchDB when a connection is available. CouchDB replication is built
   for exactly this (intermittent, conflict-tolerant sync), which is why the Community Health Toolkit and
   many health programmes use it.
2. **Event sourcing at ingestion.** Raw documents are landed immutably before anything is transformed.
   If a transformation is wrong, we fix it and replay from raw; we never lose the original submission.
3. **ELT, not ETL.** Load raw first, transform in the warehouse with dbt. Transformations are version
   controlled, tested, and reproducible.
4. **Quality as code.** Data-quality rules live next to the models as dbt tests and run on every build.
   A failing test blocks promotion to marts.
5. **Stateless services, scaled horizontally.** The API and ingestion workers hold no local state, so we
   scale them by adding replicas behind a load balancer and an autoscaler.

## How it scales to 100k users

**Collection layer (CouchDB).** Writes are absorbed by CouchDB, which is designed for high write volume
and replication. For 100k users submitting a handful of forms a day, peak write load is on the order of a
few tens of writes per second, well within a small CouchDB cluster (3 nodes, sharded databases, per-user
or per-region databases to keep replication scoped).

**Ingestion layer.** Workers consume the CouchDB `_changes` feed and checkpoint the last processed
sequence, so they are resumable and can run as multiple partitioned replicas. Throughput scales by adding
workers; back-pressure is naturally handled because the feed is pull-based.

**Warehouse + dbt.** Analytical load is decoupled from collection. dbt runs on a schedule (a Kubernetes
CronJob), incrementally where it matters, so the cost is proportional to new data, not total data.
Marts are partitioned by period and region.

**Serving layer (API + cache).** The FastAPI service is read-only over the marts and sits behind Redis.
Dashboards hit pre-aggregated marts, not raw data, so query cost stays flat as history grows. The API is
stateless and autoscaled with a `HorizontalPodAutoscaler` on CPU and request latency.

**Capacity sketch (order of magnitude, not a benchmark):**

| Layer | Bottleneck | How we scale |
|-------|-----------|--------------|
| Mobile | device storage / sync | offline queue, batched sync, per-region DBs |
| CouchDB | write + replication | 3-node sharded cluster, scoped replication |
| Ingestion | change-feed throughput | add stateless, checkpointed worker replicas |
| Warehouse | transform cost | scheduled + incremental dbt, partitioned marts |
| API | read concurrency | stateless replicas + Redis cache + HPA |

## Failure handling

- **Lost connectivity:** submissions queue on the device and sync later. Nothing is lost.
- **Worker crash:** restart resumes from the last checkpointed change sequence; ingestion is idempotent
  (documents are upserted by id + revision).
- **Bad data:** dbt tests fail the build before bad rows reach marts; the offending rows are quarantined
  and reported, not silently dropped.
- **Schema drift from forms:** staging absorbs new fields; unknown fields are kept in a raw JSON column so
  nothing is dropped before we decide how to model it.

## Security and privacy notes

Health data is sensitive. In a real deployment: encrypt in transit and at rest, scope CouchDB access per
role, keep personally identifying fields out of analytical marts (or pseudonymise them), and apply
least-privilege service accounts. No real or personal data is used anywhere in this reference project.

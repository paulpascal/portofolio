# Kubernetes deployment

Apply in order (file names are numbered):

```bash
kubectl apply -f deploy/k8s/
```

What gets created in the `health-platform` namespace:

- **config + secrets** (`00`): non-secret config as a ConfigMap; secrets as a template (create the real
  ones from a secret manager, never commit them).
- **ingestion** (`10`): the CouchDB change-feed consumer, 2 replicas, idempotent and checkpointed.
- **api** (`20`): the read-only FastAPI service, 3 replicas, with readiness/liveness probes and a
  `HorizontalPodAutoscaler` (3 to 20 pods on CPU).
- **dbt CronJob** (`30`): hourly `dbt build` (staging to intermediate to marts + tests), no overlap.
- **redis** (`40`): cache for the API.
- **ingress** (`50`): exposes the API under `/api`.

The warehouse itself is expected to be a managed Postgres (or a cloud warehouse). For a self-hosted
warehouse, add a StatefulSet with a PersistentVolumeClaim.

Images are referenced as `ghcr.io/your-username/health-platform-*`; build and push them from the
`ingestion/`, `api/` and `transform/` directories, then update the tags here.

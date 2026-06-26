# Data quality

Quality is enforced as code and runs on every `dbt build`. Three layers:

1. **Source freshness** (`_sources.yml`): warn if no new raw documents land for 12 hours, error at 36.
   Catches a stuck ingestion worker before it shows up as "missing data" in a report.
2. **Staging tests**: `not_null` and `unique` on submission id, accepted ranges on key metrics
   (households visited, stockout days). Catches malformed or out-of-range submissions early.
3. **Mart tests**: uniqueness of the `site_id + period` grain, accepted values for flags, and accepted
   ranges on percentages. Guarantees the reporting layer is internally consistent.

A failing test fails the build, so bad data cannot silently reach the marts or the dashboard.

## Beyond dbt tests

For richer profiling (distribution drift, anomaly detection on submitted values), the same warehouse can
be pointed at a profiling tool such as Great Expectations or Soda, run as a scheduled job alongside the
dbt CronJob. The principle stays the same: measure quality explicitly, block promotion on failure, and
quarantine rather than delete.

-- Staging: type and rename the raw CouchDB/ODK/Kobo form payloads.
-- We keep one row per submission and pull the fields we model; unknown fields stay in `payload`
-- so nothing is lost if a form changes before we update the model.

with raw as (
    select
        source,
        doc_id,
        rev,
        ingested_at,
        payload
    from {{ source('raw', 'documents') }}
    where payload ->> 'form' = 'chw_monthly'      -- the monthly community-health form
),

typed as (
    select
        doc_id                                              as submission_id,
        source,
        payload ->> 'site_id'                               as site_id,
        nullif(trim(payload ->> 'country'), '')             as country_raw,
        payload ->> 'period'                                as period,
        (payload -> 'metrics' ->> 'households_visited')::numeric as households_visited,
        (payload -> 'metrics' ->> 'children_screened')::numeric  as children_screened,
        (payload -> 'metrics' ->> 'referrals_made')::numeric     as referrals_made,
        (payload -> 'metrics' ->> 'stockout_days')::numeric      as stockout_days,
        (payload ->> 'target_households')::numeric          as target_households,
        (payload ->> 'submitted_at')::timestamptz           as submitted_at,
        ingested_at
    from raw
)

select
    submission_id,
    source,
    site_id,
    -- normalise country labels (trim, title case); accent handling done in intermediate
    initcap(country_raw)                                    as country,
    period,
    households_visited,
    children_screened,
    referrals_made,
    stockout_days,
    target_households,
    submitted_at,
    ingested_at
from typed

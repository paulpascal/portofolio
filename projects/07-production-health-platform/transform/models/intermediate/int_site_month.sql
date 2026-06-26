-- Intermediate: business logic. De-duplicate to one row per site and month (keep the latest
-- submission), normalise accents, and derive target attainment and a below-target flag.

with ranked as (
    select
        *,
        row_number() over (
            partition by site_id, period
            order by submitted_at desc
        ) as rn
    from {{ ref('stg_submissions') }}
),

deduped as (
    select * from ranked where rn = 1
)

select
    site_id,
    period,
    -- strip accents so "Côte d'Ivoire" and "Cote d'Ivoire" collapse to one label
    {{ strip_accents('country') }}                          as country,
    households_visited,
    children_screened,
    referrals_made,
    stockout_days,
    target_households,
    round(households_visited / nullif(target_households, 0), 3) as attainment,
    case
        when households_visited / nullif(target_households, 0) < 0.8 then 1 else 0
    end                                                     as below_target,
    submitted_at
from deduped

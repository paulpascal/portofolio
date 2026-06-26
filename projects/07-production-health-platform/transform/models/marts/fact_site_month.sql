-- Mart: the grain-level fact table, one row per site per month, ready for BI and ML.

select
    site_id,
    country,
    period,
    households_visited,
    children_screened,
    referrals_made,
    stockout_days,
    target_households,
    attainment,
    below_target
from {{ ref('int_site_month') }}

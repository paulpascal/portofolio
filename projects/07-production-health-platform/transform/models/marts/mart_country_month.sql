-- Mart: country x month reporting roll-up that powers the dashboard and the annual report.

select
    country,
    period,
    count(*)                              as sites_reporting,
    sum(households_visited)               as households_visited,
    sum(children_screened)                as children_screened,
    sum(referrals_made)                   as referrals_made,
    round(avg(attainment), 3)             as avg_attainment,
    round(avg(below_target) * 100, 1)     as pct_sites_below_target
from {{ ref('fact_site_month') }}
group by country, period

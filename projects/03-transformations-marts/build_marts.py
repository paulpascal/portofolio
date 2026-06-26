"""
Stage 03 - Transformations and marts.

Lifecycle: transformation, modelling, marts
Architecture: analytics engineering on a local warehouse (DuckDB + SQL),
              staging -> fact -> mart, the same layering you would use in dbt

Turns the curated long table into a small star-style model:
    stg_indicators     long -> one row per site/period (indicators pivoted to columns)
    fact_site_month    adds site dimensions, target attainment and a below-target flag
    mart_country_month country x month roll-up for BI and reporting

Run (after 02-cleaning-quality/clean_and_check.py):
    python build_marts.py
Outputs (Parquet, in ../_shared/data/marts/):
    fact_site_month.parquet
    mart_country_month.parquet
"""
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "_shared" / "data"
MARTS = SHARED / "marts"
MARTS.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
con.execute(f"""
CREATE VIEW curated AS SELECT * FROM read_parquet('{SHARED/"curated"/"indicators.parquet"}');
CREATE VIEW sites   AS SELECT * FROM read_csv_auto('{SHARED/"sites.csv"}');
""")

# staging: pivot indicators to columns, one row per site-period
con.execute("""
CREATE TABLE stg_indicators AS
SELECT
    site_id,
    country,
    period,
    MAX(target_households) AS target_households,
    SUM(CASE WHEN indicator='households_visited' THEN value END) AS households_visited,
    SUM(CASE WHEN indicator='children_screened'  THEN value END) AS children_screened,
    SUM(CASE WHEN indicator='referrals_made'      THEN value END) AS referrals_made,
    SUM(CASE WHEN indicator='stockout_days'       THEN value END) AS stockout_days
FROM curated
GROUP BY site_id, country, period;
""")

# fact: add site dimensions + measures
con.execute("""
CREATE TABLE fact_site_month AS
SELECT
    s.site_id,
    s.country,
    si.region,
    si.facility_type,
    s.period,
    s.households_visited,
    s.children_screened,
    s.referrals_made,
    s.stockout_days,
    s.target_households,
    ROUND(s.households_visited * 1.0 / NULLIF(s.target_households, 0), 3) AS attainment,
    CASE WHEN s.households_visited * 1.0 / NULLIF(s.target_households, 0) < 0.8
         THEN 1 ELSE 0 END AS below_target
FROM stg_indicators s
LEFT JOIN sites si USING (site_id);
""")

# mart: country x month roll-up
con.execute("""
CREATE TABLE mart_country_month AS
SELECT
    country,
    period,
    COUNT(*)                              AS sites_reporting,
    SUM(households_visited)               AS households_visited,
    SUM(children_screened)                AS children_screened,
    SUM(referrals_made)                   AS referrals_made,
    ROUND(AVG(attainment), 3)             AS avg_attainment,
    ROUND(AVG(below_target) * 100, 1)     AS pct_sites_below_target
FROM fact_site_month
GROUP BY country, period
ORDER BY country, period;
""")

con.execute(f"COPY fact_site_month   TO '{MARTS/'fact_site_month.parquet'}'   (FORMAT PARQUET);")
con.execute(f"COPY mart_country_month TO '{MARTS/'mart_country_month.parquet'}' (FORMAT PARQUET);")

f_rows = con.execute("SELECT COUNT(*) FROM fact_site_month").fetchone()[0]
m_rows = con.execute("SELECT COUNT(*) FROM mart_country_month").fetchone()[0]
print(f"Built fact_site_month ({f_rows} rows) and mart_country_month ({m_rows} rows).")
print("\nSample of mart_country_month:")
print(con.execute("""
    SELECT country, period, households_visited, avg_attainment, pct_sites_below_target
    FROM mart_country_month ORDER BY period DESC, households_visited DESC LIMIT 6
""").df().to_string(index=False))

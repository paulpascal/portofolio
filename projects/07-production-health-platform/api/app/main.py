"""
Read-only API over the marts.

Stateless FastAPI service: it only reads the dbt marts (never the raw or transactional data) and caches
hot responses in Redis. Because it is stateless and reads pre-aggregated tables, it scales horizontally
behind the Kubernetes HPA and stays fast as history grows.
"""
from __future__ import annotations
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException

try:
    import redis  # optional; the API works without it
    _r = redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))
except Exception:
    _r = None

DSN = os.environ.get("WAREHOUSE_DSN", "postgresql://wh:wh@warehouse:5432/warehouse")
MARTS = os.environ.get("MARTS_SCHEMA", "analytics_marts")
CACHE_TTL = int(os.environ.get("CACHE_TTL", "300"))

app = FastAPI(title="Health platform API", version="1.0.0")


def query(sql: str, params: tuple = ()):
    with psycopg2.connect(DSN) as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def cached(key: str, sql: str, params: tuple = ()):
    if _r:
        hit = _r.get(key)
        if hit:
            return json.loads(hit)
    rows = query(sql, params)
    if _r:
        _r.setex(key, CACHE_TTL, json.dumps(rows, default=str))
    return rows


@app.get("/health")
def health():
    try:
        query("select 1")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(503, f"warehouse unreachable: {e}")


@app.get("/countries")
def countries():
    return cached("countries", f"""
        select country, sum(households_visited) as households_visited,
               round(avg(avg_attainment), 3) as avg_attainment
        from {MARTS}.mart_country_month
        group by country order by households_visited desc
    """)


@app.get("/countries/{country}/monthly")
def country_monthly(country: str):
    rows = cached(f"cm:{country}", f"""
        select period, households_visited, children_screened,
               avg_attainment, pct_sites_below_target
        from {MARTS}.mart_country_month
        where country = %s order by period
    """, (country,))
    if not rows:
        raise HTTPException(404, "country not found")
    return rows


@app.get("/sites/at-risk")
def sites_at_risk(limit: int = 50):
    return cached(f"risk:{limit}", f"""
        select site_id, country, period, attainment, stockout_days
        from {MARTS}.fact_site_month
        where below_target = 1
        order by period desc, attainment asc
        limit %s
    """, (limit,))

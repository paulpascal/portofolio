"""
Landing layer: immutable, idempotent writes of raw documents into the warehouse.

Every source document is upserted by (source, doc_id, rev) into raw.documents as JSON.
We never mutate or delete; transformations downstream read from here and can be replayed.
A tiny checkpoint table records how far each source has been consumed so workers resume safely.
"""
from __future__ import annotations
import json
import os
import psycopg2
from psycopg2.extras import execute_values

DSN = os.environ.get("WAREHOUSE_DSN", "postgresql://wh:wh@localhost:5432/warehouse")

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.documents (
    source      text        NOT NULL,
    doc_id      text        NOT NULL,
    rev         text        NOT NULL,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    payload     jsonb       NOT NULL,
    PRIMARY KEY (source, doc_id, rev)
);
CREATE TABLE IF NOT EXISTS raw.ingestion_checkpoint (
    source     text PRIMARY KEY,
    position   text NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);
"""


def connect():
    return psycopg2.connect(DSN)


def init_storage(conn):
    with conn, conn.cursor() as cur:
        cur.execute(DDL)


def land_documents(conn, source: str, docs: list[dict]):
    """Idempotent bulk upsert. `docs` are {doc_id, rev, payload} dicts."""
    if not docs:
        return 0
    rows = [(source, d["doc_id"], d["rev"], json.dumps(d["payload"])) for d in docs]
    with conn, conn.cursor() as cur:
        execute_values(cur, """
            INSERT INTO raw.documents (source, doc_id, rev, payload)
            VALUES %s
            ON CONFLICT (source, doc_id, rev) DO NOTHING
        """, rows)
    return len(rows)


def get_checkpoint(conn, source: str) -> str | None:
    with conn.cursor() as cur:
        cur.execute("SELECT position FROM raw.ingestion_checkpoint WHERE source=%s", (source,))
        row = cur.fetchone()
        return row[0] if row else None


def set_checkpoint(conn, source: str, position: str):
    with conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO raw.ingestion_checkpoint (source, position) VALUES (%s, %s)
            ON CONFLICT (source) DO UPDATE SET position=EXCLUDED.position, updated_at=now()
        """, (source, position))

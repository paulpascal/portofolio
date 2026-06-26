"""
CouchDB ingestion: tail the _changes feed and land documents.

CouchDB's _changes feed is the backbone of offline-first sync (this is how the Community Health
Toolkit moves data from phones to the server). We consume it with a `since` checkpoint so the worker
is resumable, and we land each document immutably. Idempotency comes from the (source, id, rev) key.
"""
from __future__ import annotations
import os
import time
import requests
from landing import connect, init_storage, land_documents, get_checkpoint, set_checkpoint

SOURCE = "couchdb"
COUCH_URL = os.environ.get("COUCHDB_URL", "http://admin:password@localhost:5984")
DB = os.environ.get("COUCHDB_DB", "medic")
BATCH = int(os.environ.get("INGEST_BATCH", "200"))


def fetch_changes(since: str, limit: int):
    """One page of changes, including the full document body."""
    r = requests.get(
        f"{COUCH_URL}/{DB}/_changes",
        params={"since": since, "limit": limit, "include_docs": "true", "style": "main_only"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def run_once(conn) -> int:
    since = get_checkpoint(conn, SOURCE) or "0"
    page = fetch_changes(since, BATCH)
    docs = []
    for change in page.get("results", []):
        doc = change.get("doc") or {}
        if doc.get("_deleted"):
            continue
        docs.append({"doc_id": change["id"], "rev": doc.get("_rev", change["changes"][0]["rev"]),
                     "payload": doc})
    landed = land_documents(conn, SOURCE, docs)
    if page.get("last_seq"):
        set_checkpoint(conn, SOURCE, str(page["last_seq"]))
    return landed


def main():
    conn = connect()
    init_storage(conn)
    print(f"[couchdb] tailing {DB} from checkpoint {get_checkpoint(conn, SOURCE)}")
    while True:
        try:
            n = run_once(conn)
            if n:
                print(f"[couchdb] landed {n} documents")
            time.sleep(2 if n else 10)
        except requests.RequestException as e:
            print(f"[couchdb] transient error, backing off: {e}")
            time.sleep(15)


if __name__ == "__main__":
    main()

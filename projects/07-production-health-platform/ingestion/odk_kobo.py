"""
ODK Central / KoboToolbox ingestion.

For programmes that collect through ODK Central or KoboToolbox instead of (or alongside) CouchDB, this
puller pages through the submissions API and lands them the same way, so everything downstream is source
agnostic. Both expose an OData / submissions endpoint; we checkpoint on submission timestamp.
"""
from __future__ import annotations
import os
import requests
from landing import connect, init_storage, land_documents, get_checkpoint, set_checkpoint

PROVIDER = os.environ.get("FORMS_PROVIDER", "kobo")  # "kobo" or "odk"
TOKEN = os.environ.get("FORMS_TOKEN", "")
BASE = os.environ.get("FORMS_BASE_URL", "https://kf.kobotoolbox.org")
ASSET = os.environ.get("FORMS_ASSET_ID", "")
SOURCE = f"forms_{PROVIDER}"


def fetch_submissions(since: str | None):
    headers = {"Authorization": f"Token {TOKEN}"}
    if PROVIDER == "kobo":
        url = f"{BASE}/api/v2/assets/{ASSET}/data.json"
        params = {"sort": '{"_submission_time":1}'}
        if since:
            params["query"] = f'{{"_submission_time":{{"$gt":"{since}"}}}}'
        r = requests.get(url, headers=headers, params=params, timeout=60)
    else:  # ODK Central OData
        url = f"{BASE}/v1/projects/odata/{ASSET}.svc/Submissions"
        r = requests.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data.get("results", data.get("value", []))


def normalise(sub: dict) -> dict:
    doc_id = str(sub.get("_id") or sub.get("__id") or sub.get("meta", {}).get("instanceID"))
    rev = str(sub.get("_submission_time") or sub.get("__system", {}).get("submissionDate") or "1")
    return {"doc_id": doc_id, "rev": rev, "payload": sub}


def main():
    conn = connect()
    init_storage(conn)
    since = get_checkpoint(conn, SOURCE)
    subs = [normalise(s) for s in fetch_submissions(since)]
    landed = land_documents(conn, SOURCE, subs)
    if subs:
        set_checkpoint(conn, SOURCE, max(s["rev"] for s in subs))
    print(f"[{SOURCE}] landed {landed} submissions")


if __name__ == "__main__":
    main()

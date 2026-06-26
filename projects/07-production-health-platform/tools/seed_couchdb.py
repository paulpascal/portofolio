"""
Seed CouchDB with synthetic monthly form submissions, so the local stack has something to ingest.
Synthetic data only.
"""
import os
import random
import requests

random.seed(7)
COUCH = os.environ.get("COUCHDB_URL", "http://admin:password@localhost:5984")
DB = os.environ.get("COUCHDB_DB", "medic")
COUNTRIES = ["Togo", "Benin", "Mali", "Senegal", "Cote d'Ivoire", "Uganda", "Kenya", "Rwanda"]
MONTHS = [f"2025-{m:02d}" for m in range(1, 13)]

requests.put(f"{COUCH}/{DB}")  # create db (ok if it already exists)

docs = []
for c in COUNTRIES:
    for s in range(1, 9):
        site = f"S{c[:2].upper()}{s:02d}"
        base = random.randint(15, 45)
        quality = random.uniform(0.6, 1.4)
        for m in MONTHS:
            visits = int(base * 12 * quality * random.gauss(1, 0.08))
            docs.append({
                "_id": f"{site}-{m}",
                "form": "chw_monthly",
                "site_id": site,
                "country": c,
                "period": m,
                "target_households": base * 12,
                "submitted_at": f"{m}-15T09:00:00Z",
                "metrics": {
                    "households_visited": max(0, visits),
                    "children_screened": int(max(0, visits) * random.uniform(.5, .8)),
                    "referrals_made": random.randint(0, base),
                    "stockout_days": max(0, min(15, int((1.5 - quality) * 6))),
                },
            })

r = requests.post(f"{COUCH}/{DB}/_bulk_docs", json={"docs": docs})
print(f"Seeded {len(docs)} synthetic documents into {DB}: {r.status_code}")

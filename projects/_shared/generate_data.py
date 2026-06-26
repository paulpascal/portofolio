"""
Shared synthetic data generator for the demo projects.

Domain: a fictional multi-country community-health programme. Community health
workers submit a monthly form per site; partners report funding. NOTHING here is
real, it is all machine-generated, but it is shaped like data you actually meet:
nested submissions, missing fields, duplicates, numbers stored as text, inconsistent
country labels, and a few impossible values.

Outputs (written next to this file in ./data):
    sites.csv              reference table of sites
    submissions.jsonl      raw monthly form submissions (one JSON object per line)
    funding_raw.csv        partner funding lines

Run:
    python generate_data.py
"""
import csv
import json
import os
import random
from datetime import date

random.seed(7)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

COUNTRIES = ["Togo", "Benin", "Mali", "Senegal", "Cote d'Ivoire",
             "Uganda", "Kenya", "Rwanda", "Ghana", "Niger"]
REGION_BY_COUNTRY = {c: ("West Africa" if c in
                     ["Togo", "Benin", "Mali", "Senegal", "Cote d'Ivoire", "Ghana", "Niger"]
                     else "East Africa") for c in COUNTRIES}
FACILITY = ["health_post", "health_center", "community_site"]
MONTHS = [f"2025-{m:02d}" for m in range(1, 13)]
INDICATORS = ["households_visited", "children_screened",
              "referrals_made", "stockout_days"]

# ---- sites reference table --------------------------------------------------
sites = []
sid = 1000
for c in COUNTRIES:
    for _ in range(random.randint(5, 8)):
        sid += 1
        sites.append({
            "site_id": f"S{sid}",
            "country": c,
            "region": REGION_BY_COUNTRY[c],
            "facility_type": random.choice(FACILITY),
            "opened": f"20{random.randint(18,24)}-{random.randint(1,12):02d}-01",
        })

with open(os.path.join(DATA, "sites.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(sites[0].keys()))
    w.writeheader()
    w.writerows(sites)


def messy_country(name):
    r = random.random()
    if r < 0.06:
        return name.upper()
    if r < 0.12:
        return f"  {name} "
    if r < 0.15 and name == "Cote d'Ivoire":
        return "Côte d'Ivoire"
    return name


def dirty(v):
    """Inject the usual data-quality defects into a clean value."""
    roll = random.random()
    if roll < 0.04:
        return None                 # missing
    if roll < 0.06:
        return -abs(v)              # impossible negative
    if roll < 0.075:
        return v * 40               # outlier
    if roll < 0.10:
        return f"{v} "              # number stored as text
    return v


# ---- raw monthly submissions (nested, messy, but with a real signal) --------
# Each site has a latent, persistent performance level. Stockouts are more common
# at weaker sites, and weak sites tend to keep missing target. That persistence is
# what makes "will this site miss target next month?" genuinely predictable.
submissions = []
for s in sites:
    base = random.randint(15, 45)
    target = base * 12
    quality = random.uniform(0.6, 1.4)        # latent site performance
    for m in MONTHS:
        if random.random() < 0.05:
            continue                          # site missed a month entirely
        noise = random.gauss(1.0, 0.08)
        stockout = max(0, min(15, int(round((1.5 - quality) * 6 + random.gauss(0, 1)))))
        visits = max(0, int(round(base * 12 * quality * noise)))
        children = int(round(visits * random.uniform(0.5, 0.8)))
        referrals = random.randint(0, base)
        clean_metrics = {
            "households_visited": visits,
            "children_screened": children,
            "referrals_made": referrals,
            "stockout_days": stockout,
        }
        rec = {
            "form": "chw_monthly_v3",
            "submitted_at": f"{m}-{random.randint(2,27):02d}T09:{random.randint(0,59):02d}:00",
            "site_id": s["site_id"],
            "country": messy_country(s["country"]),
            "period": m,
            "target_households": target,
            "metrics": {k: dirty(v) for k, v in clean_metrics.items()},
            "reported_by": random.choice(["chw", "supervisor"]),
        }
        submissions.append(rec)

# duplicate a few submissions (double-submitted forms)
for d in random.sample(submissions, 18):
    submissions.append(json.loads(json.dumps(d)))
random.shuffle(submissions)

with open(os.path.join(DATA, "submissions.jsonl"), "w") as f:
    for rec in submissions:
        f.write(json.dumps(rec) + "\n")

# ---- funding lines ----------------------------------------------------------
DONOR_TYPES = ["Bilateral donor", "Multilateral fund", "Private foundation",
               "UN pooled fund", "Government co-financing"]
THEMES = ["service_delivery", "supply_chain", "data_systems", "training"]
funding = []
for _ in range(140):
    amt = random.choice([40_000, 75_000, 120_000, 300_000, 550_000, 900_000])
    roll = random.random()
    amount = "" if roll < 0.05 else (f"${amt:,}" if roll < 0.08 else amt)
    funding.append({
        "donor_type": random.choice(DONOR_TYPES),
        "region": random.choice(["West Africa", "East Africa"]),
        "country": random.choice(COUNTRIES),
        "year": random.choice([2024, 2025, 2026]),
        "theme": random.choice(THEMES),
        "amount_usd": amount,
    })
for d in random.sample(funding, 8):
    funding.append(dict(d))

with open(os.path.join(DATA, "funding_raw.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(funding[0].keys()))
    w.writeheader()
    w.writerows(funding)

print(f"Generated {len(sites)} sites, {len(submissions)} submissions, "
      f"{len(funding)} funding lines into {DATA} (synthetic).")

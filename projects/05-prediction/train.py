"""
Stage 05 - Prediction.

Lifecycle: prediction, machine learning
Architecture: supervised ML on top of the warehouse marts (scikit-learn)

Uses the site-month fact table to predict, from this month's signals, whether a
site will fall BELOW its household-visit target NEXT month. This is the kind of
early-warning model that helps a programme target support before a site slips.

Run (after 03-transformations-marts/build_marts.py):
    python train.py
Outputs:
    model_report.json   (metrics + feature importances)
    predictions.csv     (site, period, predicted risk)
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
MARTS = ROOT / "_shared" / "data" / "marts"
HERE = Path(__file__).resolve().parent

df = pd.read_parquet(MARTS / "fact_site_month.parquet")
df = df.dropna(subset=["attainment"]).copy()
# defensive guard: drop any implausible attainment that slipped through
df = df[(df["attainment"] > 0) & (df["attainment"] <= 3)].copy()
df["month_num"] = df["period"].str.slice(5, 7).astype(int)

# label = below_target in the NEXT month for the same site
df = df.sort_values(["site_id", "period"])
df["label_next"] = df.groupby("site_id")["below_target"].shift(-1)
df = df.dropna(subset=["label_next"]).copy()
df["label_next"] = df["label_next"].astype(int)

features_num = ["households_visited", "children_screened", "referrals_made",
                "stockout_days", "attainment", "month_num"]
features_cat = ["region", "facility_type"]
X = df[features_num + features_cat]
y = df["label_next"]

pre = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), features_cat),
], remainder="passthrough")
model = Pipeline([
    ("pre", pre),
    ("rf", RandomForestClassifier(n_estimators=250, max_depth=7,
                                  class_weight="balanced", random_state=0)),
])

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25,
                                          random_state=0, stratify=y)
model.fit(X_tr, y_tr)
proba = model.predict_proba(X_te)[:, 1]
pred = (proba >= 0.5).astype(int)

auc = roc_auc_score(y_te, proba)
cm = confusion_matrix(y_te, pred).tolist()

# feature importances mapped back to readable names
ohe = model.named_steps["pre"].named_transformers_["cat"]
names = list(ohe.get_feature_names_out(features_cat)) + features_num
imp = sorted(zip(names, model.named_steps["rf"].feature_importances_),
             key=lambda t: t[1], reverse=True)

report = {
    "task": "predict whether a site falls below target next month",
    "rows_used": int(len(df)),
    "positives_rate": round(float(y.mean()), 3),
    "test_roc_auc": round(float(auc), 3),
    "confusion_matrix": {"labels": ["on_track", "below_target"], "matrix": cm},
    "top_features": [{"feature": n, "importance": round(float(i), 3)} for n, i in imp[:8]],
    "note": "synthetic data; illustrative model",
}
with open(HERE / "model_report.json", "w") as f:
    json.dump(report, f, indent=2)

out = df.loc[X_te.index, ["site_id", "country", "period"]].copy()
out["risk_below_target_next"] = np.round(proba, 3)
out.sort_values("risk_below_target_next", ascending=False).to_csv(
    HERE / "predictions.csv", index=False)

print(json.dumps({k: report[k] for k in
                  ["rows_used", "positives_rate", "test_roc_auc"]}, indent=2))
print("Top features:")
for f_ in report["top_features"]:
    print(f"  {f_['feature']:<28} {f_['importance']}")
print(f"\nWrote model_report.json and predictions.csv")

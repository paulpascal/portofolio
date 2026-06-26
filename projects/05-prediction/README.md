# 05 · Prediction

**Lifecycle:** prediction · machine learning  **Architecture:** supervised ML on the warehouse marts (scikit-learn)

Predicts, from this month's signals, whether a site will fall **below its household-visit target next
month**, the kind of early-warning model that lets a programme target support before a site slips.
A random forest in a scikit-learn pipeline (one-hot for categoricals, class-balanced), evaluated with
ROC AUC and a confusion matrix, with feature importances written out.

```bash
python train.py    # -> model_report.json + predictions.csv
```

On the sample data the model reaches ~0.95 ROC AUC, with target attainment and stockout days as the
strongest predictors, which is the relationship planted in the synthetic generator. Synthetic data only.

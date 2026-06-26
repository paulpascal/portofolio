# 06 · BI dashboard

**Lifecycle:** dashboards · reporting  **Architecture:** business-intelligence layer reading the marts;
static page (no backend) so it runs on GitHub Pages

Reads the country-month mart from stage 03 (and the quality + model reports from stages 02 and 05) and
renders a small dashboard with Chart.js: households visited by country and month, average target
attainment, percentage of sites below target, and headline data-quality and model numbers.

```bash
python build_dashboard_data.py    # -> data.js
# then open index.html in a browser
```

Synthetic data only.

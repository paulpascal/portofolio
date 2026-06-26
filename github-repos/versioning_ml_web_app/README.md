# ML Model Manager

A web application for managing and training machine-learning models through a simple interface, with
data and model **versioning (DVC)** and a **continuous-integration pipeline (Jenkins)**. The focus is the
MLOps plumbing around a model: reproducible data, versioned artifacts, and automated tests, not just the
model itself.

## Features

- Upload datasets (CSV, XLSX, XLS)
- Prepare and preprocess data
- Select, configure and train models
- Visualise training results
- Version datasets and trained models with DVC (remote storage on Google Drive)
- Continuous integration with Jenkins
- Clean, responsive UI

## Stack

| Layer | Technology |
|------|------------|
| Backend | Python, Flask |
| Frontend | HTML, Tailwind / DaisyUI |
| Data | pandas |
| ML | scikit-learn |
| Versioning | Git + DVC (Google Drive remote) |
| CI | Jenkins |

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # set SECRET_KEY, UPLOAD_FOLDER, DVC_REMOTE_URL, credentials path
dvc init && dvc remote add -d myremote gdrive://<folder-id>
python -m app.main          # http://localhost:5000
```

## Tests

```bash
pytest                       # unit tests
pytest --cov=app tests/      # with coverage
```

## What it demonstrates

The MLOps side of a model-training app: a clean Flask service, reproducible data and model versioning
with DVC, and an automated CI pipeline, so training runs are repeatable and artifacts are tracked rather
than lost.

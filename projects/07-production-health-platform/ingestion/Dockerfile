FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# default: tail CouchDB; override the command for the ODK/Kobo puller
CMD ["python", "couchdb_changes.py"]

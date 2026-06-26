.PHONY: up down build dbt logs seed

up:            ## start the full local stack
	docker compose up --build -d

down:          ## stop everything
	docker compose down

dbt:           ## run the models + tests
	docker compose run --rm dbt dbt deps
	docker compose run --rm dbt dbt build

logs:          ## tail ingestion logs
	docker compose logs -f ingestion

seed:          ## load synthetic demo documents into CouchDB
	python tools/seed_couchdb.py

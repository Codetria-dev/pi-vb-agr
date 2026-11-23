SHELL := /bin/bash
COMPOSE := docker compose -f infra/docker-compose.yml

.PHONY: up down logs status collect mock upload hive datasets dashboard pipeline reset check

up:
	$(COMPOSE) up -d --build

down:
	bash scripts/07_parar.sh

logs:
	$(COMPOSE) logs -f --tail=100

status:
	bash scripts/99_status.sh

check:
	bash scripts/00_verificar_ambiente.sh

collect:
	bash scripts/01_coleta.sh

mock:
	bash scripts/01_coleta.sh --mock

upload:
	bash scripts/02_upload_bronze.sh

hive:
	bash scripts/03_hive_layers.sh

datasets:
	bash scripts/05_superset_datasets.sh

dashboard:
	bash scripts/08_criar_dashboard.sh

pipeline:
	bash scripts/04_pipeline_completo.sh

reset:
	bash scripts/07_parar.sh --volumes

#!/usr/bin/env bash
# Pipeline completo:
#   coleta -> stack Docker -> HDFS (Bronze) -> Hive (Silver/Gold) -> datasets Superset
#
# Uso:
#   APIFY_TOKEN=... bash scripts/04_pipeline_completo.sh
#   bash scripts/04_pipeline_completo.sh --mock
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/_compose.sh"
DC=(docker compose -f "$AGR_COMPOSE")

bash scripts/00_verificar_ambiente.sh

echo ""
echo "============================================================"
echo " ETAPA 1/6 - Coleta (Apify ou mock)"
echo "============================================================"
bash scripts/01_coleta.sh "$@"

echo ""
echo "============================================================"
echo " ETAPA 2/6 - Subindo a stack Docker"
echo "============================================================"
"${DC[@]}" up -d --build

echo ""
echo "============================================================"
echo " ETAPA 3/6 - Enviando dados para o HDFS (Bronze)"
echo "============================================================"
bash scripts/02_upload_bronze.sh

echo ""
echo "============================================================"
echo " ETAPA 4/6 - Processando HiveQL (Silver + Gold)"
echo "============================================================"
bash scripts/03_hive_layers.sh

echo ""
echo "============================================================"
echo " ETAPA 5/6 - Registrando datasets no Superset"
echo "============================================================"
echo "[superset] aguardando http://localhost:8088 ..."
for _ in $(seq 1 60); do
  if curl -fsS http://localhost:8088/health >/dev/null 2>&1; then
    break
  fi
  sleep 5
done
bash scripts/05_superset_datasets.sh

echo ""
echo "============================================================"
echo " ETAPA 6/6 - Criando graficos e dashboard no Superset"
echo "============================================================"
bash scripts/08_criar_dashboard.sh

echo ""
echo "============================================================"
echo " PIPELINE CONCLUIDO"
echo "============================================================"
echo "HDFS     : http://localhost:9870"
echo "Trino    : http://localhost:8080"
echo "Superset : http://localhost:8088  (admin / admin)"
echo "Dashboard: http://localhost:8088/superset/dashboard/agr-engajamento-digital/"
echo ""
echo "Valide no Trino:"
echo "  python scripts/06_consultar_trino.py \"SELECT * FROM hive.gold.kpis\""

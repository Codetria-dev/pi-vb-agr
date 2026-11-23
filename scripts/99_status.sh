#!/usr/bin/env bash
# Mostra o estado da stack e os endereços úteis.
set -euo pipefail
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_compose.sh"

docker compose -f "$AGR_COMPOSE" ps

cat <<'EOF'

Endereços:
  HDFS NameNode      http://localhost:9870
  HiveServer2 UI     http://localhost:10002
  Trino              http://localhost:8080
  Superset           http://localhost:8088  (admin/admin por padrão)

Atalhos:
  HDFS:     docker compose -f infra/docker-compose.yml exec namenode hdfs dfs -ls -R /lake
  Trino:    docker compose -f infra/docker-compose.yml exec trino trino
  Beeline:  docker compose -f infra/docker-compose.yml exec hive-server beeline -u jdbc:hive2://localhost:10000/
  Pipeline: bash scripts/04_pipeline_completo.sh
  Consulta: python scripts/06_consultar_trino.py "SELECT * FROM hive.gold.kpis"
  Parar:    bash scripts/07_parar.sh
EOF

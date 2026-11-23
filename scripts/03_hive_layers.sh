#!/usr/bin/env bash
# Executa as camadas HiveQL: Bronze -> Silver -> Gold.
set -euo pipefail
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_compose.sh"
DC=(docker compose -f "$AGR_COMPOSE")
BEELINE=("${DC[@]}" exec -T hive-server /opt/hive/bin/beeline -u jdbc:hive2://localhost:10000 -n hive)

echo "[hive] aguardando o HiveServer2 (pode levar 1-3 minutos)..."
PRONTO=0
for _ in $(seq 1 80); do
  if "${BEELINE[@]}" -e "SELECT 1" >/dev/null 2>&1; then
    PRONTO=1
    break
  fi
  sleep 5
done

if [ "$PRONTO" -ne 1 ]; then
  echo "ERRO: HiveServer2 nao respondeu."
  echo "Veja os logs: docker compose -f infra/docker-compose.yml logs hive-server hive-metastore"
  exit 1
fi

for SCRIPT in 00_databases.sql 01_bronze.sql 02_silver.sql 03_gold.sql; do
  echo ""
  echo "============================================================"
  echo "[hive] executando $SCRIPT"
  echo "============================================================"
  "${BEELINE[@]}" --silent=true --showHeader=false -f "/hive/$SCRIPT"
done

echo ""
echo "[hive] camadas Bronze, Silver e Gold criadas com sucesso."

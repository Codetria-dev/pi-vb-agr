#!/usr/bin/env bash
# Cria os gráficos e o dashboard da AGR no Superset (dados Gold via Trino).
set -euo pipefail
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_compose.sh"
DC=(docker compose -f "$AGR_COMPOSE")

echo "[superset] aguardando o container responder..."
PRONTO=0
for _ in $(seq 1 60); do
  if "${DC[@]}" exec -T superset python -c "import superset" >/dev/null 2>&1; then
    PRONTO=1
    break
  fi
  sleep 5
done
if [ "$PRONTO" -ne 1 ]; then
  echo "ERRO: container superset nao respondeu."
  exit 1
fi

"${DC[@]}" exec -T superset \
  python /app/pythonpath/create_dashboard.py

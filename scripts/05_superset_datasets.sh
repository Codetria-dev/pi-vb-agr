#!/usr/bin/env bash
# Registra os datasets Gold no Superset (execute depois do script 04).
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
  echo "Veja: docker compose -f infra/docker-compose.yml logs superset superset-init"
  exit 1
fi

"${DC[@]}" exec -T superset \
  python /app/pythonpath/bootstrap_datasets.py

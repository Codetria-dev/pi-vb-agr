#!/usr/bin/env bash
# Coleta Instagram + Google Maps via Apify e grava JSON Lines em dados/.
#
# Uso:
#   APIFY_TOKEN=apify_api_... bash scripts/01_coleta.sh
#   bash scripts/01_coleta.sh --mock          # sem chamar o Apify
#
# Sem token (ou em caso de falha/limite do Apify), o script usa o fallback
# sintetico de coleta/gerar_mock.py para o pipeline nao travar na apresentacao.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! python -c "import apify_client" >/dev/null 2>&1; then
  echo "[aviso] apify-client nao instalado (pip install -r coleta/requirements.txt)."
  echo "[aviso] O pipeline vai usar dados mock se o token nao puder ser usado."
fi

# Sem -I: o apify-client pode estar instalado no site-packages do usuário.
python coleta/coletar_dados.py "$@"

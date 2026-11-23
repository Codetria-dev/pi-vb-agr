#!/usr/bin/env bash
# Para a stack. Use --volumes para apagar também os dados persistidos.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/scripts/_compose.sh"
docker compose -f "$AGR_COMPOSE" down "$@"

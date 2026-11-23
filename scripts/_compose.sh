#!/usr/bin/env bash
# Helper comum (source): garante o docker no PATH e resolve o caminho do
# Compose para o Docker CLI do Windows, que nao entende /c/... .
# Requer que a variavel ROOT ja esteja definida.

if ! command -v docker >/dev/null 2>&1; then
  for DOCKER_BIN in \
    "/c/Program Files/Docker/Docker/resources/bin" \
    "/mnt/c/Program Files/Docker/Docker/resources/bin"; do
    if [ -x "$DOCKER_BIN/docker" ] || [ -x "$DOCKER_BIN/docker.exe" ]; then
      export PATH="$DOCKER_BIN:$PATH"
      break
    fi
  done
fi

if command -v cygpath >/dev/null 2>&1; then
  AGR_COMPOSE="$(cygpath -w "$ROOT/infra/docker-compose.yml")"
else
  AGR_COMPOSE="$ROOT/infra/docker-compose.yml"
fi

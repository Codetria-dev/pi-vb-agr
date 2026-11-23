#!/usr/bin/env bash
# Verifica se o ambiente tem o necessario para rodar o pipeline.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "============================================================"
echo " Verificacao de ambiente - Pipeline Big Data AGR"
echo "============================================================"

echo ""
echo "[1/3] Python"
if command -v python >/dev/null 2>&1; then
  python --version
else
  echo "ERRO: Python nao encontrado no PATH."
  exit 1
fi

echo ""
echo "[2/3] Docker"
if ! command -v docker >/dev/null 2>&1; then
  echo "ERRO: Docker nao encontrado."
  echo "Instale o Docker Desktop: https://www.docker.com/products/docker-desktop/"
  exit 1
fi
docker --version
docker compose version

echo ""
echo "[3/3] Recursos do Docker"
docker info --format 'RAM total: {{.MemTotal}} bytes | CPUs: {{.NCPU}}' || true

echo ""
echo "OK. Arquivos principais:"
ls -1 README.md Makefile infra/docker-compose.yml hive/ coleta/ | head -40

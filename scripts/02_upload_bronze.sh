#!/usr/bin/env bash
# Envia os JSON Lines da coleta para o HDFS em /lake/bronze/.
set -euo pipefail
# Git Bash converte /dados e /lake para caminhos Windows; desabilita.
export MSYS_NO_PATHCONV=1

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
source "$ROOT/scripts/_compose.sh"
DC=(docker compose -f "$AGR_COMPOSE")

for ARQUIVO in dados/dados_instagram.json dados/dados_google.json \
               dados/dados_instagram_perfil.json dados/dados_google_local.json; do
  if [ ! -s "$ARQUIVO" ]; then
    echo "ERRO: $ARQUIVO nao encontrado ou vazio. Rode: bash scripts/01_coleta.sh"
    exit 1
  fi
done

echo "[hdfs] aguardando o NameNode..."
PRONTO=0
for _ in $(seq 1 60); do
  if "${DC[@]}" exec -T namenode hdfs dfs -ls / >/dev/null 2>&1; then
    PRONTO=1
    break
  fi
  sleep 3
done

if [ "$PRONTO" -ne 1 ]; then
  echo "ERRO: NameNode nao respondeu. Veja: docker compose -f infra/docker-compose.yml logs namenode"
  exit 1
fi

echo "[hdfs] criando diretorios da camada Bronze..."
"${DC[@]}" exec -T namenode hdfs dfs -mkdir -p \
  /lake/bronze/instagram \
  /lake/bronze/google \
  /lake/bronze/instagram_perfil \
  /lake/bronze/google_local

echo "[hdfs] enviando arquivos..."
"${DC[@]}" exec -T namenode hdfs dfs -put -f \
  /dados/dados_instagram.json \
  /lake/bronze/instagram/dados_instagram.json

"${DC[@]}" exec -T namenode hdfs dfs -put -f \
  /dados/dados_google.json \
  /lake/bronze/google/dados_google.json

"${DC[@]}" exec -T namenode hdfs dfs -put -f \
  /dados/dados_instagram_perfil.json \
  /lake/bronze/instagram_perfil/dados_instagram_perfil.json

"${DC[@]}" exec -T namenode hdfs dfs -put -f \
  /dados/dados_google_local.json \
  /lake/bronze/google_local/dados_google_local.json

echo "[hdfs] conteudo de /lake/bronze:"
"${DC[@]}" exec -T namenode hdfs dfs -ls -R /lake/bronze

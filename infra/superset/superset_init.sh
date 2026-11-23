#!/usr/bin/env bash
set -euo pipefail

echo "[superset-init] Aplicando migrações..."
superset db upgrade

echo "[superset-init] Garantindo usuário administrador..."
superset fab create-admin \
  --username "${SUPERSET_ADMIN_USER:-admin}" \
  --firstname "AGR" \
  --lastname "Admin" \
  --email "${SUPERSET_ADMIN_EMAIL:-admin@agr.local}" \
  --password "${SUPERSET_ADMIN_PASSWORD:-admin}" || true

echo "[superset-init] Inicializando Superset..."
superset init

echo "[superset-init] Registrando a conexão com o Trino..."
superset set-database-uri \
  -d "Trino AGR" \
  -u "trino://admin@trino:8080/hive" || true

echo "[superset-init] Concluído."

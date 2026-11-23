#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${DATA_DIR:-/opt/hadoop/data/data}"
mkdir -p "$DATA_DIR"

echo "[datanode] Iniciando DataNode em $DATA_DIR ..."
exec hdfs datanode

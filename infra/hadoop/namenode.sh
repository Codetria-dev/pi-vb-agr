#!/usr/bin/env bash
set -euo pipefail

NAME_DIR="${NAME_DIR:-/opt/hadoop/data/name}"
mkdir -p "$NAME_DIR"

if [ ! -f "$NAME_DIR/current/VERSION" ]; then
  echo "[namenode] Formatando o NameNode em $NAME_DIR ..."
  hdfs namenode -format -force -nonInteractive
fi

echo "[namenode] Iniciando NameNode..."
exec hdfs namenode

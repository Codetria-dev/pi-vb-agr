#!/usr/bin/env python3
"""Executa uma consulta SQL no Trino via REST API, sem precisar do CLI.

Uso:
    python scripts/06_consultar_trino.py
    python scripts/06_consultar_trino.py "SELECT * FROM hive.gold.kpis"
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

TRINO = "http://localhost:8080"
USUARIO = "admin"


def _requisicao(url: str, sql: str | None = None) -> dict:
    dados = sql.encode("utf-8") if sql is not None else None
    req = urllib.request.Request(
        url,
        data=dados,
        method="POST" if sql is not None else "GET",
        headers={
            "X-Trino-User": USUARIO,
            "X-Trino-Catalog": "hive",
            "X-Trino-Schema": "gold",
            "Content-Type": "text/plain",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def executar(sql: str) -> int:
    try:
        payload = _requisicao(f"{TRINO}/v1/statement", sql)
    except urllib.error.URLError as exc:
        print(f"ERRO: nao foi possivel conectar ao Trino em {TRINO}: {exc}")
        print("O container 'agr-trino' esta rodando? Use: docker compose ps")
        return 1

    while True:
        if payload.get("error"):
            erro = payload["error"]
            print(f"ERRO Trino: {erro.get('message')}")
            return 1

        colunas = payload.get("columns")
        if colunas:
            print(" | ".join(c.get("name", "") for c in colunas))
            print("-" * 80)

        for linha in payload.get("data") or []:
            print(" | ".join("" if v is None else str(v) for v in linha))

        proxima = payload.get("nextUri")
        if not proxima:
            break

        try:
            payload = _requisicao(proxima)
        except urllib.error.URLError as exc:
            print(f"ERRO ao buscar proxima pagina: {exc}")
            return 1
        time.sleep(0.2)

    return 0


def main() -> int:
    sql = " ".join(sys.argv[1:]).strip()
    if not sql:
        sql = "SELECT * FROM hive.gold.kpis ORDER BY metrica"
    print(f"-- SQL: {sql}\n")
    return executar(sql)


if __name__ == "__main__":
    raise SystemExit(main())

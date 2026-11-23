#!/usr/bin/env python3
"""Coleta dados da AGR no Instagram e no Google Maps via Apify.

Saidas (JSON Lines, um objeto por linha, UTF-8 sem BOM):
    dados/dados_instagram.json
    dados/dados_google.json
    dados/metadados.json
    dados/raw/*.json            (respostas brutas do Apify, para auditoria)

Uso:
    python coleta/coletar_dados.py
    python coleta/coletar_dados.py --mock
    python coleta/coletar_dados.py --instagram-limit 50 --google-max-reviews 50

O token e lido de APIFY_TOKEN (.env ou variavel de ambiente) e nunca e gravado.
Em caso de falha/limite do Apify, o script cai automaticamente para dados mock.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
RAW = DADOS / "raw"

# Permite importar normalizar/gerar_mock ao rodar o arquivo diretamente.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from gerar_mock import (  # noqa: E402
    gerar_posts_instagram,
    gerar_reviews_google,
    metadados_mock,
)
from normalizar import (  # noqa: E402
    metadados_local_google,
    metadados_perfil_instagram,
    normalizar_post_instagram,
    normalizar_review_google,
)

URL_GOOGLE_PADRAO = (
    "https://www.google.com/maps/place/AGR+-+Ag%C3%AAncia+Goiana+de+"
    "Regula%C3%A7%C3%A3o,+Controle+e+Fiscaliza%C3%A7%C3%A3o+de+Servi%C3%A7os+"
    "P%C3%BAblicos/@-16.674483,-49.2620082,540m/data=!3m1!1e3!4m8!3m7!1s"
    "0x935ef165d5ee7c1b:0x45fa9798dad53b14!8m2!3d-16.6771466!4d-49.2577108"
    "!9m1!1b1!16s%2Fg%2F1pw3ytrlb?entry=ttu"
)


def carregar_env(caminho: Path) -> None:
    """Carrega um .env simples sem depender de python-dotenv."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        os.environ.setdefault(chave, valor)


def _int_env(nome: str, padrao: int) -> int:
    try:
        return int(os.getenv(nome, str(padrao)))
    except ValueError:
        return padrao


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Coleta de dados da AGR via Apify")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Forca a geracao de dados sinteticos (nao chama o Apify).",
    )
    parser.add_argument(
        "--instagram-limit",
        type=int,
        default=_int_env("INSTAGRAM_POSTS_LIMIT", 50),
        help="Quantidade maxima de posts do Instagram (padrao: 50).",
    )
    parser.add_argument(
        "--google-max-reviews",
        type=int,
        default=_int_env("GOOGLE_MAX_REVIEWS", 50),
        help="Quantidade maxima de avaliacoes do Google (padrao: 50).",
    )
    parser.add_argument(
        "--instagram-url",
        default=os.getenv("AGR_INSTAGRAM_URL", "https://www.instagram.com/agrgoias/"),
    )
    parser.add_argument(
        "--google-url",
        default=os.getenv("AGR_GOOGLE_MAPS_URL", URL_GOOGLE_PADRAO),
    )
    return parser.parse_args()


def salvar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def salvar_ndjson(caminho: Path, registros: list[dict]) -> None:
    """Grava JSON Lines: um objeto por linha (formato lido pelo Hive)."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8", newline="\n") as fh:
        for registro in registros:
            fh.write(json.dumps(registro, ensure_ascii=False) + "\n")


def deduplicar(registros: list[dict]) -> list[dict]:
    vistos: set[str] = set()
    unicos: list[dict] = []
    for registro in registros:
        chave = str(registro.get("id") or "")
        if chave and chave in vistos:
            continue
        if chave:
            vistos.add(chave)
        unicos.append(registro)
    return unicos


def coletar_via_apify(token: str, args: argparse.Namespace) -> dict:
    """Executa os atores do Apify e devolve dados brutos + normalizados."""
    try:
        from apify_client import ApifyClient
    except ImportError as exc:  # pragma: no cover - depende do ambiente
        raise RuntimeError(
            "apify-client nao instalado. Rode: pip install -r coleta/requirements.txt"
        ) from exc

    client = ApifyClient(token)

    print("[apify] Instagram: coletando perfil...", flush=True)
    run_perfil = client.actor("apify/instagram-scraper").call(
        run_input={
            "directUrls": [args.instagram_url],
            "resultsType": "details",
        }
    )
    perfil_raw = list(client.dataset(run_perfil["defaultDatasetId"]).iterate_items())
    perfil = perfil_raw[0] if perfil_raw else {}

    print("[apify] Instagram: coletando posts...", flush=True)
    run_posts = client.actor("apify/instagram-scraper").call(
        run_input={
            "directUrls": [args.instagram_url],
            "resultsType": "posts",
            "resultsLimit": args.instagram_limit,
        }
    )
    posts_raw = list(client.dataset(run_posts["defaultDatasetId"]).iterate_items())

    print("[apify] Google Maps: coletando local e avaliacoes...", flush=True)
    run_google = client.actor("compass/crawler-google-places").call(
        run_input={
            "startUrls": [{"url": args.google_url}],
            "maxCrawledPlacesPerSearch": 1,
            "language": "pt-BR",
            "countryCode": "br",
            "scrapePlaceDetailPage": True,
            "maxReviews": args.google_max_reviews,
            "scrapeReviewsPersonalData": False,
            "maxImages": 0,
            "scrapeContacts": False,
            "includeWebResults": False,
        }
    )
    locais_raw = list(client.dataset(run_google["defaultDatasetId"]).iterate_items())
    local = locais_raw[0] if locais_raw else {}
    reviews_raw = local.get("reviews") or []

    return {
        "perfil": perfil,
        "posts": posts_raw,
        "local": local,
        "reviews": reviews_raw,
        "raw": {
            "instagram_perfil": perfil_raw,
            "instagram_posts": posts_raw,
            "google_maps": locais_raw,
        },
    }


def coletar_mock(args: argparse.Namespace) -> tuple[dict, list[dict], list[dict]]:
    metadados = metadados_mock()
    posts = gerar_posts_instagram(args.instagram_limit)
    reviews = gerar_reviews_google(args.google_max_reviews)
    return metadados, posts, reviews


def main() -> int:
    carregar_env(RAIZ / ".env")
    args = parse_args()
    DADOS.mkdir(parents=True, exist_ok=True)

    origem = {"instagram": "mock", "google_maps": "mock"}
    metadados = metadados_mock()
    posts: list[dict] = []
    reviews: list[dict] = []

    if args.mock:
        print("[mock] --mock informado: gerando dados sinteticos.", flush=True)
        metadados, posts, reviews = coletar_mock(args)
    else:
        token = os.getenv("APIFY_TOKEN", "").strip()
        token_invalido = token in {"", "apify_api_seu_token_aqui"}
        if token_invalido:
            print(
                "[aviso] APIFY_TOKEN nao configurado. "
                "Gerando dados mock para o pipeline nao travar.",
                flush=True,
            )
            metadados, posts, reviews = coletar_mock(args)
        else:
            try:
                bruto = coletar_via_apify(token, args)
                salvar_json(RAW / "instagram_perfil.json", bruto["raw"]["instagram_perfil"])
                salvar_json(RAW / "instagram_posts.json", bruto["raw"]["instagram_posts"])
                salvar_json(RAW / "google_maps.json", bruto["raw"]["google_maps"])

                posts = [
                    normalizar_post_instagram(p) for p in bruto["posts"]
                ]
                reviews = [
                    normalizar_review_google(r, bruto["local"].get("url", ""))
                    for r in bruto["reviews"]
                ]
                metadados = {
                    "coletado_em": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                    "instagram": metadados_perfil_instagram(bruto["perfil"])
                    if bruto["perfil"]
                    else metadados_mock()["instagram"],
                    "google_maps": metadados_local_google(bruto["local"])
                    if bruto["local"]
                    else metadados_mock()["google_maps"],
                }
                origem = {"instagram": "apify", "google_maps": "apify"}
                print(
                    f"[apify] Coleta concluida: {len(posts)} posts, "
                    f"{len(reviews)} avaliacoes.",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001 - fallback proposital
                print(f"[erro] Falha na coleta via Apify: {exc}", flush=True)
                print(
                    "[fallback] Gerando dados mock para nao travar o pipeline.",
                    flush=True,
                )
                metadados, posts, reviews = coletar_mock(args)

    # Limpeza minima: registros sem data nao entram no data lake.
    posts = [p for p in posts if p.get("data")]
    reviews = [r for r in reviews if r.get("data")]

    # Fallback por plataforma caso o Apify tenha retornado vazio.
    if not posts:
        print("[aviso] Nenhum post do Instagram; usando mock.", flush=True)
        posts = gerar_posts_instagram(args.instagram_limit)
        origem["instagram"] = "mock"
    if not reviews:
        print("[aviso] Nenhuma avaliacao do Google; usando mock.", flush=True)
        reviews = gerar_reviews_google(args.google_max_reviews)
        origem["google_maps"] = "mock"

    posts = deduplicar(posts)
    reviews = deduplicar(reviews)
    for indice, registro in enumerate(posts):
        registro["id"] = registro.get("id") or f"instagram_{indice}"
    for indice, registro in enumerate(reviews):
        registro["id"] = registro.get("id") or f"google_{indice}"

    metadados["origem"] = origem
    metadados["coletado_em"] = metadados.get("coletado_em") or datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")
    metadados["totais"] = {
        "instagram": len(posts),
        "google_maps": len(reviews),
    }

    salvar_ndjson(DADOS / "dados_instagram.json", posts)
    salvar_ndjson(DADOS / "dados_google.json", reviews)
    salvar_json(DADOS / "metadados.json", metadados)

    # Perfil e dados do local tambem viram JSON Lines (1 registro), para que
    # o Hive consiga ler as metricas de seguidores/nota media.
    perfil_nd = metadados.get("instagram") or {}
    local_nd = metadados.get("google_maps") or {}
    salvar_ndjson(DADOS / "dados_instagram_perfil.json", [perfil_nd] if perfil_nd else [])
    salvar_ndjson(DADOS / "dados_google_local.json", [local_nd] if local_nd else [])

    print("", flush=True)
    print(f"Instagram : {len(posts):>3} registros  (origem: {origem['instagram']})")
    print(f"Google    : {len(reviews):>3} registros  (origem: {origem['google_maps']})")
    print(f"Arquivos  : {DADOS / 'dados_instagram.json'}")
    print(f"            {DADOS / 'dados_google.json'}")
    print(f"Metadados : {DADOS / 'metadados.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

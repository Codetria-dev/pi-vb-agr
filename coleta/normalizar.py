"""Normalizacao dos dados brutos do Apify para o schema unico em portugues.

Schema de saida (usado pelas tabelas Bronze/Silver do Hive):

    id | plataforma | tipo | texto | data | curtidas | comentarios |
    nota | autor | url | tipo_midia
"""
from __future__ import annotations


def _texto(valor) -> str:
    return str(valor).strip() if valor is not None else ""


def _inteiro(valor, padrao=0):
    try:
        if valor is None or valor == "":
            return padrao
        return int(float(valor))
    except (TypeError, ValueError):
        return padrao


def normalizar_post_instagram(post: dict) -> dict:
    """Converte um item do ator apify/instagram-scraper (resultsType=posts)."""
    return {
        "id": str(post.get("id") or post.get("shortCode") or ""),
        "plataforma": "instagram",
        "tipo": "post",
        "texto": _texto(post.get("caption")),
        "data": _texto(post.get("timestamp")),
        "curtidas": _inteiro(post.get("likesCount")),
        "comentarios": _inteiro(post.get("commentsCount")),
        "nota": None,
        "autor": _texto(post.get("ownerUsername")) or "agrgoias",
        "url": _texto(post.get("url")),
        "tipo_midia": _texto(post.get("type")),
    }


def normalizar_review_google(review: dict, url_local: str = "") -> dict:
    """Converte uma review do ator compass/crawler-google-places."""
    nota = review.get("stars")
    return {
        "id": str(review.get("reviewId") or review.get("id") or ""),
        "plataforma": "google_maps",
        "tipo": "avaliacao",
        "texto": _texto(review.get("text") or review.get("textTranslated")),
        "data": _texto(review.get("publishedAtDate") or review.get("publishAt")),
        "curtidas": _inteiro(review.get("likesCount")),
        "comentarios": 0,
        "nota": _inteiro(nota, None) if nota is not None else None,
        "autor": _texto(review.get("name") or review.get("reviewerName")) or "Anônimo",
        "url": _texto(review.get("reviewUrl")) or url_local,
        "tipo_midia": "avaliacao",
    }


def metadados_perfil_instagram(perfil: dict) -> dict:
    return {
        "usuario": _texto(perfil.get("username")),
        "nome": _texto(perfil.get("fullName")),
        "biografia": _texto(perfil.get("biography")),
        "seguidores": _inteiro(perfil.get("followersCount")),
        "seguindo": _inteiro(perfil.get("followsCount")),
        "posts": _inteiro(perfil.get("postsCount")),
        "verificado": bool(perfil.get("verified")),
        "categoria": _texto(perfil.get("businessCategoryName")),
        "site": _texto(perfil.get("externalUrl")),
        "url": _texto(perfil.get("url")),
    }


def metadados_local_google(local: dict) -> dict:
    loc = local.get("location") or {}
    return {
        "nome": _texto(local.get("title")),
        "categoria": _texto(local.get("categoryName")),
        "endereco": _texto(local.get("address")),
        "bairro": _texto(local.get("neighborhood")),
        "cidade": _texto(local.get("city")),
        "estado": _texto(local.get("state")),
        "cep": _texto(local.get("postalCode")),
        "telefone": _texto(local.get("phone")),
        "site": _texto(local.get("website")),
        "nota_media": local.get("totalScore"),
        "total_avaliacoes": _inteiro(local.get("reviewsCount")),
        "latitude": loc.get("lat"),
        "longitude": loc.get("lng"),
        "place_id": _texto(local.get("placeId")),
        "url": _texto(local.get("url")),
    }

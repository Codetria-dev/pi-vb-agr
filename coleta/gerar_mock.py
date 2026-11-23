"""Gera dados sinteticos realistas para o fallback do pipeline.

Usado quando:
  * o token do Apify nao esta configurado;
  * a conta gratuita estourou o limite;
  * o scraping falhou no dia da apresentacao.

Os registros seguem exatamente o mesmo schema dos dados reais, portanto o
restante do pipeline (HDFS -> Hive -> Trino -> Superset) nao muda.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

TEMAS_INSTAGRAM = [
    (
        "transporte",
        "A AGR fiscaliza o transporte rodoviario intermunicipal de passageiros "
        "e orienta a populacao sobre seus direitos.",
    ),
    (
        "onibus",
        "Fiscalizacao de onibus intermunicipais: veja como denunciar "
        "irregularidades a AGR.",
    ),
    (
        "agua",
        "Agua da chuva nao e esgoto. Entenda a diferenca entre drenagem "
        "pluvial e rede de esgotamento sanitario.",
    ),
    (
        "esgoto",
        "A AGR acompanha os investimentos em esgotamento sanitario e cobra "
        "a melhoria do atendimento a populacao.",
    ),
    (
        "energia",
        "Reajuste tarifario de energia: a AGR participa da discussao e "
        "fiscaliza a qualidade do servico da Enel.",
    ),
    (
        "enel",
        "Ouvidoria e AGR acompanham reclamacoes sobre a Enel em Goias. "
        "Saiba como registrar sua demanda.",
    ),
    (
        "atendimento",
        "Atendimento ao cidadao: a Ouvidoria da AGR recebe denuncias e "
        "sugestoes sobre servicos publicos.",
    ),
    (
        "tarifa",
        "Tarifa de onibus e agua: a AGR avalia os pedidos de reajuste com "
        "base nos contratos de concessao.",
    ),
    (
        "fiscalizacao",
        "Equipes da AGR realizam vistorias e fiscalizacoes em unidades de "
        "saude e empresas de transporte.",
    ),
    (
        "saude",
        "Vistorias em hospitais estaduais avaliam conservacao e manutencao "
        "das estruturas fisicas.",
    ),
    (
        "ouvidoria",
        "A Ouvidoria da Mulher Servidora acolhe denuncias de assedio e "
        "discriminacao no servico publico.",
    ),
    (
        "servico",
        "Servicos publicos essenciais: a AGR regula, controla e fiscaliza "
        "a prestacao em Goias.",
    ),
]

HASHTAGS = [
    "#AGR",
    "#Goias",
    "#ServicosPublicos",
    "#Regulacao",
    "#Fiscalizacao",
    "#GovernoDeGoias",
]

REVIEWS_POSITIVAS = [
    "Atendimento excelente, equipe muito atenciosa e prestativa.",
    "A AGR tem feito um trabalho importante na fiscalizacao dos onibus intermunicipais.",
    "Otimo atendimento pelo telefone. Resolveram minha duvida sobre a tarifa.",
    "A fiscalizacao da agua e do esgoto melhorou muito na nossa regiao.",
    "Parabens pelo atendimento da ouvidoria, responderam rapido.",
    "Servico publico de qualidade e equipe comprometida com a populacao.",
]
REVIEWS_NEUTRAS = [
    "Atendimento razoavel, mas demorou um pouco para responder.",
    "O local e de facil acesso, porem o estacionamento e complicado.",
    "Servico ok, nada excepcional.",
    "Fui atendido, mas ainda aguardo retorno sobre a reclamacao da Enel.",
]
REVIEWS_NEGATIVAS = [
    "Pessimo atendimento, ninguem resolve nada pelo telefone.",
    "A fiscalizacao dos onibus nao funciona. Os veiculos continuam lotados.",
    "Demora enorme para responder a ouvidoria. Falta retorno sobre a Enel.",
    "A agua continua com problema e ninguem fiscaliza de verdade.",
    "Muito burocratico e pouco transparente com a populacao.",
    "Nao resolvem as reclamacoes sobre esgoto e atendimento.",
]


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def gerar_posts_instagram(quantidade: int = 50):
    """Gera posts sinteticos no schema normalizado."""
    rng = random.Random(42)
    agora = datetime.now(timezone.utc)
    registros = []

    for i in range(quantidade):
        tema, frase = rng.choice(TEMAS_INSTAGRAM)
        hashtags = " ".join(rng.sample(HASHTAGS, k=rng.randint(1, 3)))
        extra = rng.choice(
            [
                "",
                " Confira os detalhes no site agr.go.gov.br.",
                " Acompanhe nossas acoes e participe da fiscalizacao.",
                " A regulacao existe para proteger o cidadao.",
            ]
        )
        tipo_midia = rng.choices(
            ["Image", "Video", "Sidecar"], weights=[0.45, 0.25, 0.30], k=1
        )[0]

        curtidas = rng.randint(12, 180)
        if tipo_midia == "Video":
            curtidas += rng.randint(0, 90)
        comentarios = rng.choices(
            [0, 1, 2, 3, 5, 8, 12, 20],
            weights=[0.25, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.04],
            k=1,
        )[0]

        dt = (agora - timedelta(days=rng.randint(0, 180))).replace(
            hour=rng.choice([8, 9, 10, 11, 12, 14, 15, 16, 17, 18]),
            minute=rng.randint(0, 59),
            second=0,
            microsecond=0,
        )

        registros.append(
            {
                "id": f"mock_ig_{i:04d}",
                "plataforma": "instagram",
                "tipo": "post",
                "texto": f"{frase}{extra} {hashtags}".strip(),
                "data": _iso(dt),
                "curtidas": curtidas,
                "comentarios": comentarios,
                "nota": None,
                "autor": "agrgoias",
                "url": f"https://www.instagram.com/agrgoias/",
                "tipo_midia": tipo_midia,
            }
        )

    registros.sort(key=lambda r: r["data"], reverse=True)
    return registros


def gerar_reviews_google(quantidade: int = 32):
    """Gera avaliacoes sinteticas com distribuicao parecida com a real da AGR."""
    rng = random.Random(7)
    agora = datetime.now(timezone.utc)
    registros = []

    for i in range(quantidade):
        estrelas = rng.choices([1, 2, 3, 4, 5], weights=[0.40, 0.04, 0.05, 0.06, 0.45], k=1)[0]
        if estrelas >= 4:
            texto = rng.choice(REVIEWS_POSITIVAS)
        elif estrelas == 3:
            texto = rng.choice(REVIEWS_NEUTRAS)
        else:
            texto = rng.choice(REVIEWS_NEGATIVAS)

        # Nem toda avaliacao tem comentario, igual ao Google real.
        if rng.random() < 0.30:
            texto = ""

        dt = (agora - timedelta(days=rng.randint(0, 365))).replace(
            hour=rng.randint(7, 21), minute=rng.randint(0, 59), second=0, microsecond=0
        )

        registros.append(
            {
                "id": f"mock_gm_{i:04d}",
                "plataforma": "google_maps",
                "tipo": "avaliacao",
                "texto": texto,
                "data": _iso(dt),
                "curtidas": 0,
                "comentarios": 0,
                "nota": estrelas,
                "autor": "Anônimo",
                "url": "",
                "tipo_midia": "avaliacao",
            }
        )

    registros.sort(key=lambda r: r["data"], reverse=True)
    return registros


def metadados_mock() -> dict:
    """Metadados sinteticos equivalentes aos retornados pelo Apify."""
    return {
        "coletado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "origem": "mock",
        "instagram": {
            "usuario": "agrgoias",
            "nome": "Agência Goiana de Regulação",
            "biografia": (
                "Agência Goiana de Regulação, Controle e Fiscalização de "
                "Serviços Públicos - Governo de Goiás"
            ),
            "seguidores": 5411,
            "seguindo": 177,
            "posts": 50,
            "verificado": True,
            "categoria": "Government organization",
            "site": "http://www.agr.go.gov.br/",
            "url": "https://www.instagram.com/agrgoias",
        },
        "google_maps": {
            "nome": (
                "AGR - Agência Goiana de Regulação, Controle e Fiscalização "
                "de Serviços Públicos"
            ),
            "categoria": "Repartição pública",
            "endereco": "Av. Goiás, 305 - St. Central, Goiânia - GO, 74005-010, Brasil",
            "bairro": "Setor Central",
            "cidade": "Goiânia",
            "estado": "Goiás",
            "cep": "74005-010",
            "telefone": "+55 62 3226-6400",
            "site": "https://www.agr.go.gov.br/",
            "nota_media": 3.2,
            "total_avaliacoes": 32,
            "latitude": -16.6771466,
            "longitude": -49.2577108,
            "place_id": "ChIJG3zu1WXxXpMRFDvV2piX-kU",
            "url": (
                "https://www.google.com/maps/place/AGR+-+Ag%C3%AAncia+Goiana+"
                "de+Regula%C3%A7%C3%A3o"
            ),
        },
    }

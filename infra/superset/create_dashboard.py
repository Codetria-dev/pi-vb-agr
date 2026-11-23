"""Cria os gráficos e o dashboard da AGR no Superset (dataset Gold via Trino).

Executar dentro do container, depois do bootstrap dos datasets:
    docker compose -f infra/docker-compose.yml exec -T superset \
        python /app/pythonpath/create_dashboard.py

Idempotente: remove o dashboard/gráficos de mesmo nome antes de recriar.
"""
import json
import sys

SLUG = "agr-engajamento-digital"
TITLE = "AGR — Engajamento Digital"


def _params(**kwargs):
    base = {
        "time_range": "No filter",
        "granularity_sqla": None,
        "row_limit": 50000,
    }
    base.update(kwargs)
    base["viz_type"] = kwargs["viz_type"]
    return base


def _kpi(name, metrica, subheader):
    return {
        "name": name,
        "dataset": "kpis",
        # big_number_total e o plugin moderno e nao exige coluna temporal.
        "viz_type": "big_number_total",
        "params": _params(
            viz_type="big_number_total",
            metric="sum_valor",
            adhoc_filters=[
                {
                    "clause": "WHERE",
                    "expressionType": "SIMPLE",
                    "subject": "metrica",
                    "operator": "==",
                    "comparator": metrica,
                    "isExtra": False,
                }
            ],
            subheader=subheader,
            y_axis_format="SMART_NUMBER",
            header_font_size=0.4,
            subheader_font_size=0.15,
        ),
    }


def _pie(name, dataset, groupby, metric, row_limit=20):
    return {
        "name": name,
        "dataset": dataset,
        "viz_type": "pie",
        "params": _params(
            viz_type="pie",
            groupby=[groupby],
            metric=metric,
            row_limit=row_limit,
            show_legend=True,
            show_labels=True,
        ),
    }


def _table(name, dataset, columns, row_limit=50):
    return {
        "name": name,
        "dataset": dataset,
        "viz_type": "table",
        "params": _params(
            viz_type="table",
            query_mode="raw",
            all_columns=columns,
            adhoc_filters=[],
            order_by_cols=[],
            row_limit=row_limit,
        ),
    }


CHARTS = [
    _kpi("AGR — Seguidores Instagram", "seguidores_instagram", "Seguidores"),
    _kpi("AGR — Posts Instagram", "total_posts_instagram", "Posts"),
    _kpi("AGR — Avaliações Google", "total_avaliacoes_google", "Avaliações"),
    _kpi("AGR — Taxa de Engajamento", "taxa_engajamento_pct", "Taxa de engajamento (%)"),
    _pie("AGR — Sentimento das Avaliações", "sentimento_google", "sentimento", "sum_total"),
    _pie("AGR — Temas Mais Citados", "temas", "tema", "sum_mencoes", row_limit=10),
    _pie(
        "AGR — Distribuição das Notas",
        "google_maps_avaliacoes_por_nota",
        "stars",
        "sum_reviews",
        row_limit=10,
    ),
    _pie(
        "AGR — Engajamento por Tipo de Mídia",
        "engajamento_tipo_midia",
        "tipo_midia",
        "avg_media_curtidas",
        row_limit=10,
    ),
    _table(
        "AGR — Top Posts por Engajamento",
        "instagram_top_posts",
        ["post_type", "caption", "likes_count", "comments_count", "engagement_rate_pct"],
        row_limit=20,
    ),
    _table(
        "AGR — Avaliações Recentes",
        "google_maps_avaliacoes_recentes",
        ["published_at", "stars", "reviewer_name", "review_text"],
    ),
    _table(
        "AGR — Evolução Temporal",
        "evolucao_temporal",
        ["ano_mes", "plataforma", "total", "total_curtidas", "total_comentarios",
         "media_engajamento"],
    ),
    _table(
        "AGR — Engajamento por Plataforma",
        "engajamento_plataforma",
        ["plataforma", "tipo", "total_registros", "media_curtidas",
         "media_comentarios", "media_engajamento"],
    ),
]

# metric_name, expressão SQL, rótulo
METRICS = {
    "kpis": [("sum_valor", "SUM(valor)", "Soma de valor")],
    "sentimento_google": [("sum_total", "SUM(total)", "Total de avaliações")],
    "temas": [("sum_mencoes", "SUM(mencoes)", "Menções")],
    "google_maps_avaliacoes_por_nota": [
        ("sum_reviews", "SUM(reviews)", "Avaliações")
    ],
    "engajamento_tipo_midia": [
        ("avg_media_curtidas", "AVG(media_curtidas)", "Média de curtidas")
    ],
}


def _ensure_metrics(datasets, db, SqlMetric):
    for table_name, metrics in METRICS.items():
        dataset = datasets[table_name]
        existing = {metric.metric_name for metric in dataset.metrics}
        for metric_name, expression, verbose_name in metrics:
            if metric_name in existing:
                continue
            dataset.metrics.append(
                SqlMetric(
                    metric_name=metric_name,
                    expression=expression,
                    verbose_name=verbose_name,
                )
            )
            print(f"[metric] {table_name}.{metric_name}")
    db.session.commit()


def _position(charts):
    by_name = {chart.slice_name: chart for chart in charts}
    rows = [
        [
            "AGR — Seguidores Instagram",
            "AGR — Posts Instagram",
            "AGR — Avaliações Google",
            "AGR — Taxa de Engajamento",
        ],
        [
            "AGR — Sentimento das Avaliações",
            "AGR — Temas Mais Citados",
            "AGR — Distribuição das Notas",
            "AGR — Engajamento por Tipo de Mídia",
        ],
        [
            "AGR — Top Posts por Engajamento",
            "AGR — Avaliações Recentes",
        ],
        [
            "AGR — Evolução Temporal",
            "AGR — Engajamento por Plataforma",
        ],
    ]

    position = {
        "DASHBOARD_VERSION_KEY": "v2",
        "HEADER_ID": {"id": "HEADER_ID", "type": "HEADER", "meta": {"text": TITLE}},
        "ROOT_ID": {"id": "ROOT_ID", "type": "ROOT", "children": ["GRID_ID"]},
        "GRID_ID": {
            "id": "GRID_ID",
            "type": "GRID",
            "parents": ["ROOT_ID"],
            "children": [],
        },
    }

    for index, names in enumerate(rows, start=1):
        row_id = f"ROW-{index}"
        position[row_id] = {
            "id": row_id,
            "type": "ROW",
            "parents": ["ROOT_ID", "GRID_ID"],
            "children": [],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        width = 3 if len(names) == 4 else 6
        for name in names:
            chart = by_name[name]
            chart_id = f"CHART-{chart.id}"
            position[chart_id] = {
                "id": chart_id,
                "type": "CHART",
                "parents": ["ROOT_ID", "GRID_ID", row_id],
                "children": [],
                "meta": {
                    "chartId": chart.id,
                    "uuid": str(chart.uuid),
                    "sliceName": name,
                    "width": width,
                    "height": 50,
                },
            }
            position[row_id]["children"].append(chart_id)
        position["GRID_ID"]["children"].append(row_id)

    return position


def main():
    from superset.app import create_app

    app = create_app()
    with app.app_context():
        from superset import db, security_manager
        from superset.connectors.sqla.models import SqlaTable, SqlMetric
        from superset.models.dashboard import Dashboard
        from superset.models.slice import Slice
        from superset.utils.core import DatasourceType

        datasets = {
            dataset.table_name: dataset
            for dataset in db.session.query(SqlaTable).filter_by(schema="gold").all()
        }
        missing = {spec["dataset"] for spec in CHARTS} - set(datasets)
        if missing:
            sys.exit(f"Datasets ausentes no Superset: {sorted(missing)}")

        _ensure_metrics(datasets, db, SqlMetric)

        # Recria do zero para manter nomes/IDs consistentes.
        existing_dash = db.session.query(Dashboard).filter_by(slug=SLUG).first()
        if existing_dash:
            db.session.delete(existing_dash)
            db.session.flush()
        names = [spec["name"] for spec in CHARTS]
        for old in db.session.query(Slice).filter(Slice.slice_name.in_(names)).all():
            db.session.delete(old)
        db.session.commit()

        owner = security_manager.get_user_by_id(1)
        charts = []
        for spec in CHARTS:
            dataset = datasets[spec["dataset"]]
            chart = Slice(
                slice_name=spec["name"],
                viz_type=spec["viz_type"],
                datasource_id=dataset.id,
                datasource_type=DatasourceType.TABLE,
                params=json.dumps(spec["params"]),
                owners=[owner],
            )
            db.session.add(chart)
            charts.append(chart)
        db.session.commit()

        dashboard = Dashboard()
        dashboard.dashboard_title = TITLE
        dashboard.slug = SLUG
        dashboard.published = True
        dashboard.owners = [owner]
        dashboard.json_metadata = json.dumps(
            {
                "label_colors": {
                    "Positivo": "#2ca02c",
                    "Neutro": "#ff7f0e",
                    "Negativo": "#d62728",
                }
            }
        )
        dashboard.position_json = json.dumps(_position(charts))
        dashboard.slices = charts
        db.session.add(dashboard)
        db.session.commit()

        print(f"[ok] dashboard '{TITLE}' (slug={SLUG})")
        print(f"[ok] {len(charts)} gráficos criados")
        for chart in charts:
            print(f"  - {chart.id}: {chart.slice_name} ({chart.viz_type})")


if __name__ == "__main__":
    main()

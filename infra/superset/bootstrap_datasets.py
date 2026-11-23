"""Cria datasets do Superset apontando para as tabelas Gold no Trino.

Executar depois que as tabelas Gold existirem:
    docker compose -f infra/docker-compose.yml exec -T superset \
        python /app/pythonpath/bootstrap_datasets.py
"""
import os
import sys

DB_NAME = os.environ.get("SUPERSET_TRINO_DB_NAME", "Trino AGR")
CATALOG = os.environ.get("SUPERSET_TRINO_CATALOG", "hive")
SCHEMA = os.environ.get("SUPERSET_GOLD_SCHEMA", "gold")
TABLES = [
    "engajamento_plataforma",
    "sentimento_google",
    "temas",
    "frequencia_engajamento",
    "evolucao_temporal",
    "engajamento_tipo_midia",
    "kpis",
    "instagram_top_posts",
    "google_maps_avaliacoes_por_nota",
    "google_maps_avaliacoes_recentes",
]


def main() -> None:
    # Os imports do Superset precisam ocorrer depois do app context.
    from superset.app import create_app

    app = create_app()
    with app.app_context():
        from superset.connectors.sqla.models import SqlaTable
        from superset.extensions import db
        from superset.models.core import Database

        database = (
            db.session.query(Database)
            .filter_by(database_name=DB_NAME)
            .one_or_none()
        )
        if database is None:
            sys.exit(
                f"Conexão '{DB_NAME}' não encontrada. Rode o superset-init primeiro."
            )

        created = 0
        for table_name in TABLES:
            exists = (
                db.session.query(SqlaTable)
                .filter_by(
                    table_name=table_name,
                    schema=SCHEMA,
                    database_id=database.id,
                )
                .first()
            )
            if exists:
                print(f"[skip] {SCHEMA}.{table_name}")
                continue

            table = SqlaTable(
                table_name=table_name,
                schema=SCHEMA,
                catalog=CATALOG,
                database=database,
            )
            table.fetch_metadata()
            db.session.add(table)
            db.session.commit()
            created += 1
            print(f"[ok] {SCHEMA}.{table_name}")

        print(f"{created} dataset(s) criado(s).")


if __name__ == "__main__":
    main()

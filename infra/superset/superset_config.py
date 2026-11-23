import os

# Chave usada para assinar cookies/sessões. Troque em produção.
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "dev-only-change-me")

# Metadados do Superset (dashboard, datasets, usuários) no PostgreSQL.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://hive:hive@postgres:5432/superset"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Ambiente de laboratório servido em HTTP.
TALISMAN_ENABLED = False
ENABLE_PROXY_FIX = True
SESSION_COOKIE_SAMESITE = "Lax"

# Timeouts maiores para consultas no Trino.
SQLLAB_TIMEOUT = 300
SUPERSET_WEBSERVER_TIMEOUT = 300

FEATURE_FLAGS = {
    "DASHBOARD_RBAC": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

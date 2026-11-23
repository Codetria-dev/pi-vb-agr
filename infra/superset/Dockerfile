FROM apache/superset:5.0.0

USER root

# A imagem "lean" usa um virtualenv em /app/.venv e nao instala os extras
# [postgres]. Instalamos o driver PostgreSQL e o dialeto do Trino no venv
# correto (via uv), sem tocar no pin de requests do Superset.
RUN uv pip install --python /app/.venv/bin/python \
    "psycopg2-binary==2.9.6" \
    "trino[sqlalchemy]==0.335.0"

USER superset

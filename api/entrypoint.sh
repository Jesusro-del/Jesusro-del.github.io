#!/bin/sh
# Espera a que Postgres acepte conexiones y ya tenga la tabla del libro.
# Si todavía no está, reintenta: el proceso no termina ni deja a gunicorn sirviendo a ciegas.
set -e

python - <<'PY'
import os
import sys
import time

import psycopg

for _ in range(30):
    try:
        with psycopg.connect(
            host=os.environ.get("DB_HOST", "db"),
            port=os.environ.get("DB_PORT", "5432"),
            dbname=os.environ.get("DB_NAME", "libro"),
            user=os.environ.get("DB_USER", "app"),
            password=os.environ.get("DB_PASSWORD", ""),
            connect_timeout=3,
        ) as con:
            con.execute("SELECT 1 FROM mensajes LIMIT 0")
        sys.exit(0)
    except psycopg.Error:
        time.sleep(1)

sys.exit(1)
PY

exec gunicorn --bind "0.0.0.0:${PORT:-3000}" --workers 2 --access-logfile - --error-logfile - app:app

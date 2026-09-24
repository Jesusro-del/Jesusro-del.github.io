# API del libro de visitas.
# La imagen no lleva contraseñas: gunicorn lee PORT y la app lee DB_* al arrancar.
# El builder instala dependencias en un venv. Esa etapa no llega a la imagen final.
FROM python:3.12-slim-trixie AS builder

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /opt/venv/bin/pip uninstall -y pip setuptools wheel

# Runtime: intérprete slim, el venv y app.py. Sin pip, ni compiladores, ni caché.
FROM python:3.12-slim-trixie

WORKDIR /app

RUN useradd --create-home --uid 1000 --shell /usr/sbin/nologin app \
    && python -m pip uninstall -y pip setuptools wheel \
    && rm -rf /root/.cache /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app app.py entrypoint.sh .
RUN chmod 755 /app/entrypoint.sh

ENV PATH="/opt/venv/bin:$PATH"

USER app

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT','3000'))"

CMD ["sh", "/app/entrypoint.sh"]

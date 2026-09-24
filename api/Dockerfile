# API del libro de visitas.
# La imagen no lleva contraseñas: gunicorn lee PORT y la app lee DB_* al arrancar.
FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin app

COPY --chown=app:app app.py .

USER app

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/api/health' % os.environ.get('PORT','3000'))"

CMD gunicorn --bind 0.0.0.0:${PORT:-3000} --workers 2 --access-logfile - --error-logfile - app:app

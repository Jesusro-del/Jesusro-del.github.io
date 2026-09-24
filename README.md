# Perfil — Luis Jesús David Razo Oliva
Sitio personal publicado en https://Jesusro-del.github.io

## Cómo se publica
Cada push a `main` despliega automáticamente con GitHub Pages.

## Flujo de trabajo
- `main` protegida; todo cambio entra por pull request
- Una rama por cambio: `feature/*`, `fix/*`
- Mensajes de commit en imperativo, ≤ 50 caracteres

## Historial del curso
- **S02** — Sitio inicial, ramas y pull requests

## Cómo levantar el libro de visitas

```bash
cp .env.example .env
# Editar .env y escribir DB_PASSWORD. Ese archivo no se sube.
docker compose up --build
```

El sitio queda en http://localhost:8080. La base no publica puerto: solo nginx sale al host.

En un Codespace nuevo no hace falta copiar `.env` ni escribir comandos. `.devcontainer/devcontainer.json` crea `.env` con una contraseña local (no se commitea) la primera vez y, en cada arranque, ejecuta `docker compose up -d --build --wait`. Al terminar de cargar, web, api y db quedan sanos y el puerto 8080 se abre en el navegador.

## Bitácora de decisiones

- **Tres servicios.** `web` sirve el HTML de la raíz, `api` corre gunicorn y `db` es Postgres 16. El HTML sigue en la raíz porque GitHub Pages lo necesita ahí; la imagen de nginx solo lo copia.
- **Mismo origen.** El navegador llama a `/api`. nginx reenvía esa ruta al servicio `api` usando `PORT` de `.env`. No hay URL ni puerto en `libro-de-visitas.js`.
- **Dos redes.** `frontal` une web y api. `datos` une api y db. Postgres no está en `frontal` ni tiene `ports`: desde el host no se alcanza.
- **Credenciales.** La contraseña vive solo en `.env` (gitignored) y entra a Postgres como `POSTGRES_PASSWORD` al arrancar. `.env.example` se commitea con `DB_PASSWORD` vacío. Los `.dockerignore` dejan `.env` fuera de las imágenes.
- **Datos.** El volumen `datos` guarda `/var/lib/postgresql/data`. `docker compose down` no lo borra; hace falta `docker compose down -v` para empezar de cero. Los SQL de `db/init/` corren solo con el volumen vacío.
- **Salud.** `db` usa `pg_isready`. `api` pide `GET /api/health`, que falla si no habla con la base. `web` pide ese mismo health a través del proxy. Cada uno espera al anterior con `condition: service_healthy`.
- **Proceso de la API.** La imagen final es `python:3.12-slim-bookworm` en dos etapas: el builder instala el venv y la etapa final solo copia ese venv y `app.py`. Arranca gunicorn con el usuario `app`. El código de ejecución es `/app`. El editor del Codespace es un contenedor aparte; el volumen `.:/workspace` solo monta el repo dentro de `api`.

## Bitácora de decisiones (LAB-02)

### Reto 1: Imagen mínima

- **Decisión:** El Dockerfile de `api` tiene dos etapas. El builder (`python:3.12-slim-bookworm`) crea `/opt/venv`, instala Flask, gunicorn y `psycopg[binary]`, y desinstala pip. La etapa final es la misma base slim: copia solo el venv y `app.py`, quita pip del sistema y corre como `app`.
- **Alternativas que evalué:**
  - `python:3.12` en una sola etapa. Pro: funciona a la primera y las ruedas manylinux instalan sin compilar. Contra: la imagen pesa 1.17 GB porque arrastra Debian completo, pip y la caché del instalador.
  - `python:3.12-alpine`. Pro: la base pesa mucho menos. Contra: `psycopg[binary]` publica ruedas glibc; en musl hay que compilar, y la imagen final se queda con librerías frágiles o con el compilador.
  - Distroless. Pro: no trae shell ni gestor de paquetes. Contra: el `CMD` de gunicorn expande `${PORT}` con un shell, y sin shell el healthcheck y el arranque dejan de funcionar como están escritos.
- **Por qué elegí esta:** Slim en dos etapas baja de 1.17 GB a 154 MB (menos de la mitad) y la etapa final no contiene `gcc` ni `pip`. La rueda binaria de psycopg corre sobre glibc, así que no hace falta un compilador en ninguna etapa que se publique.
- **Fuentes consultadas:**
  - https://docs.docker.com/build/building/multi-stage/
  - https://hub.docker.com/_/python
  - https://www.psycopg.org/psycopg3/docs/basic/install.html
  - https://github.com/GoogleContainerTools/distroless
  - https://github.com/wagoodman/dive
- **Cómo lo verifiqué:** La ingenua es una sola etapa `FROM python:3.12` con `pip install` (no está en el repo; se construyó con un Dockerfile temporal). La final es `docker build --load -t libro-api:min api`.

```
docker images libro-api
IMAGE                                ID             DISK USAGE   CONTENT SIZE   EXTRA
docker.io/library/libro-api:min      1a480885e327        154MB             0B
docker.io/library/libro-api:naive    9ed68fd688a8       1.17GB             0B
```

154 MB es menos de la mitad de 1.17 GB. `docker history libro-api:min` muestra que lo que añade este Dockerfile es el venv (20.3 MB) y `app.py` (4.61 kB); no hay una capa de `apt-get install gcc`:

```
docker history libro-api:min
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
1a480885e327   2 seconds ago    CMD ["/bin/sh" "-c" "gunicorn --bind 0.0.0.0…   0B        buildkit.dockerfile.v0
<missing>      2 seconds ago    HEALTHCHECK {Test:[CMD-SHELL python -c "impo…   0B        buildkit.dockerfile.v0
<missing>      2 seconds ago    EXPOSE [3000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      2 seconds ago    USER app                                        0B        buildkit.dockerfile.v0
<missing>      2 seconds ago    ENV PATH=/opt/venv/bin:/usr/local/bin:/usr/l…   0B        buildkit.dockerfile.v0
<missing>      2 seconds ago    COPY --chown=app:app app.py . # buildkit        4.61kB    buildkit.dockerfile.v0
<missing>      2 seconds ago    COPY /opt/venv /opt/venv # buildkit             20.3MB    buildkit.dockerfile.v0
<missing>      57 seconds ago   RUN /bin/sh -c useradd --create-home --uid 1…   4.28MB    buildkit.dockerfile.v0
<missing>      59 seconds ago   WORKDIR /app                                    1.54kB    buildkit.dockerfile.v0
<missing>      5 days ago       CMD ["python3"]                                 0B        buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;  for src in idle3 p…   5.12kB    buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;   savedAptMark="$(a…   41.6MB    buildkit.dockerfile.v0
<missing>      5 days ago       ENV PYTHON_SHA256=5c8462af5790baf43a321a1559…   0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV PYTHON_VERSION=3.12.14                      0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV GPG_KEY=7169605F62C751356D054A26A821E680…   0B        buildkit.dockerfile.v0
<missing>      5 days ago       RUN /bin/sh -c set -eux;  apt-get update;  a…   9.6MB     buildkit.dockerfile.v0
<missing>      5 days ago       ENV LANG=C.UTF-8                                0B        buildkit.dockerfile.v0
<missing>      5 days ago       ENV PATH=/usr/local/bin:/usr/local/sbin:/usr…   0B        buildkit.dockerfile.v0
<missing>      6 days ago       # debian.sh --arch 'amd64' out/ 'bookworm' '…   77.9MB    debuerreotype 0.17
```

Dentro de la imagen final, `gcc` y `pip` no están, y Flask, gunicorn y psycopg importan:

```
docker run --rm --user root --entrypoint python libro-api:min -c "import shutil; print('gcc', shutil.which('gcc')); print('pip', shutil.which('pip')); import gunicorn, flask, psycopg; print('imports-ok')"
gcc None
pip None
imports-ok
```

- **Qué no me funcionó:** El primer `docker build` usó el driver `docker-container` sin `--load`: el build terminó bien, pero `docker images` no mostró la etiqueta porque la imagen se quedó en la caché de BuildKit. Había que repetir el build con `--load`. Además, la primera imagen de dos etapas seguía trayendo pip dentro del venv; desinstalarlo solo en el sistema no bastaba. Hay que quitarlo en el builder, antes de copiar `/opt/venv`.
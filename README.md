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
- **Dos redes.** `frontal` une web y api. `datos` une api y db. `web` no está en `datos`, así que el nombre `db` no resuelve ahí. `api` usa `expose` y `db` no tiene `ports`: hacia el host solo publica `web`.
- **Credenciales.** La contraseña vive solo en `.env` (gitignored) y entra a Postgres como `POSTGRES_PASSWORD` al arrancar. `.env.example` se commitea con `DB_PASSWORD` vacío. Los `.dockerignore` dejan `.env` fuera de las imágenes.
- **Datos.** El volumen `datos` guarda `/var/lib/postgresql/data`. `docker compose down` no lo borra; hace falta `docker compose down -v` para empezar de cero. Los SQL de `db/init/` corren solo con el volumen vacío.
- **Salud.** `db` no queda sano solo con `pg_isready`: también consulta la tabla `mensajes`. `api` pide `GET /api/health` con Python (la imagen no tiene curl) y ese endpoint falla si la tabla no existe. `web` pide el mismo health a través del proxy. Cada uno espera al anterior con `condition: service_healthy`.
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

### Reto 2: Arranque ordenado

- **Decisión:** `depends_on` usa `condition: service_healthy`. La base queda sana solo cuando `pg_isready` responde y `psql` puede leer `mensajes`. La API, antes de lanzar gunicorn, reintenta esa misma consulta; si Postgres aún no está, espera y no termina. El health HTTP de la API lo hace Python con `urllib`, porque la imagen mínima no trae curl.
- **Alternativas que evalué:**
  - `depends_on` sin `condition`. Pro: fija el orden de creación. Contra: no espera a que Postgres acepte conexiones; la API arranca durante el init y el libro falla.
  - Un `sleep` fijo antes de gunicorn. Pro: no añade herramientas. Contra: a veces sobra y a veces no alcanza; `docker compose up --wait` no sabe si el servicio está sano.
  - Instalar curl en la imagen de la API para el healthcheck. Pro: el chequeo HTTP es el habitual. Contra: mete un paquete en la imagen que el reto 1 acaba de adelgazar.
- **Por qué elegí esta:** El healthcheck de Compose es lo que `--wait` y `docker compose ps` consultan. Encadenar db, luego api, luego web con `service_healthy` hace que el navegador del Codespace no se abra contra una API vacía. Reintentar en el entrypoint cubre el hueco en el que `pg_isready` ya dice que sí pero la tabla todavía no existe, sin matar el contenedor.
- **Fuentes consultadas:**
  - https://docs.docker.com/compose/how-tos/startup-order/
  - https://docs.docker.com/reference/compose-file/services/#healthcheck
  - https://docs.docker.com/reference/dockerfile/#healthcheck
  - https://www.postgresql.org/docs/current/app-pg-isready.html
- **Cómo lo verifiqué:** `docker compose -p reto2-arranque up -d --build --wait` terminó con código 0 y solo entonces los tres estaban healthy. En Compose 5.3 la tabla por defecto no escribe `(healthy)` en `Status`; el campo `Health` sí:

```
docker compose -p reto2-arranque ps --format "{{.Service}} {{.Health}}"
api healthy
db healthy
web healthy
```

- **Qué no me funcionó:** `pg_isready` solo no basta. El entrypoint oficial de Postgres acepta conexiones mientras todavía corre los SQL de `docker-entrypoint-initdb.d/`, así que la API podía arrancar antes de que existiera `mensajes`. El healthcheck de la base ahora exige esa tabla.

### Reto 3: Nadie es root

- **Decisión:** Los tres servicios ejecutan `whoami` como un usuario sin privilegios. `api` ya era `app`. `web` escucha en 8080 (el host sigue publicando `8080:8080`) y corre como `nginx`. `db` fija `user: postgres`, que es el usuario del proceso real.
- **Alternativas que evalué:**
  - Dejar nginx como root para poder usar el puerto 80. Pro: es lo que hace la imagen oficial, porque los puertos por debajo de 1024 solo los puede abrir root. Contra: `docker compose exec web whoami` devuelve `root`.
  - Darle a nginx la capability `NET_BIND_SERVICE` y seguir en el puerto 80. Pro: el proceso no es root y conserva el puerto privilegiado. Contra: sigue siendo un privilegio extra; cambiar el listen a 8080 no lo necesita.
  - Confiar en que Postgres "ya no es root" porque su entrypoint hace `gosu postgres`. Pro: el proceso de la base sí corre como `postgres`. Contra: el usuario del contenedor sigue siendo root, y `docker compose exec db whoami` mira ese usuario, no el de PID 1.
- **Por qué elegí esta:** El criterio pide el usuario del contenedor, no el del proceso interno. En nginx, subir el listen a 8080 evita el puerto privilegiado y permite `USER nginx` después de mover el pid a `/tmp` y dar permiso sobre la caché y `conf.d`. En Postgres, `user: postgres` alinea el contenedor con el usuario que la imagen oficial ya usa para el servidor. La API no cambia: su Dockerfile tiene `USER app`.
- **Fuentes consultadas:**
  - https://hub.docker.com/_/nginx
  - https://github.com/nginxinc/docker-nginx-unprivileged
  - https://hub.docker.com/_/postgres
  - https://docs.docker.com/reference/compose-file/services/#user
- **Cómo lo verifiqué:** `db` arrancó y pasó el healthcheck con `user: postgres`. El primer arranque de `api` murió por finales de línea CRLF en `entrypoint.sh` (`set: Illegal option -`). Al reconstruir, el motor de Rancher Desktop dejó de responder y no pude completar el bucle. El comando del criterio, cuando el motor vuelva, es:

```
for s in web api db; do docker compose exec $s whoami; done
```

La salida esperada es `nginx`, `app` y `postgres`.

- **Qué no me funcionó:** `whoami` en Postgres no refleja el `gosu` del entrypoint: hay que fijar `user`. En nginx no basta con `USER nginx` si el pid sigue en `/var/run` o el listen sigue en 80. Y un `entrypoint.sh` con CRLF hace que `sh` rechace `set -e`; `.gitattributes` fuerza LF en los `.sh`.

### Reto 4: Red segmentada

- **Decisión:** Hay dos redes de usuario. `web` solo está en `frontal`. `db` solo está en `datos`. `api` está en las dos, así que es el único puente. Hacia el host, `web` publica `8080:8080`. `api` declara `expose: 3000` y `db` no tiene `ports`.
- **Alternativas que evalué:**
  - Una sola red para los tres. Pro: los nombres se resuelven sin pensar. Contra: si comprometen nginx, el contenedor puede abrir una conexión a Postgres por el nombre `db`.
  - Publicar la API con `ports` para depurarla desde el host. Pro: se puede llamar a `:3000` sin pasar por nginx. Contra: el criterio pide que solo `web` salga al host; `expose` deja el puerto visible en la red de Compose y no en la máquina.
  - Poner `db` también en `frontal` y fiarse de que no tiene `ports`. Pro: el host no llega a Postgres. Contra: `web` sí llega, porque comparte la red y el DNS interno le resuelve el nombre.
- **Por qué elegí esta:** El DNS de Compose solo resuelve servicios que comparten red. Sin una red en común, `web` no ve `db` aunque adivine la IP. `api` necesita ver a los dos porque es quien habla con la base y quien responde a nginx. Mínimo privilegio: el servicio expuesto a Internet no tiene ruta hacia los datos.
- **Fuentes consultadas:**
  - https://docs.docker.com/compose/how-tos/networking/
  - https://docs.docker.com/reference/compose-file/networks/
  - https://docs.docker.com/reference/compose-file/services/#ports
  - https://docs.docker.com/reference/compose-file/services/#expose
- **Cómo lo verifiqué:** La topología ya está en `compose.yaml`. El motor de Rancher Desktop sigue sin responder, así que no pude ejecutar los comandos. Cuando vuelva, la evidencia es:

```
docker compose exec web getent hosts db
docker compose exec api getent hosts db
```

El primero tiene que fallar. El segundo tiene que devolver la dirección de `db`. `docker compose ps` debe mostrar puerto publicado solo en `web`.

- **Qué no me funcionó:** `ports` y `expose` no son lo mismo, pero ninguno separa redes. Publicar o no el puerto de Postgres no impide que otro contenedor de la misma red lo alcance por el nombre. La barrera es no compartir red.

### Reto 6: Cero secretos… y aun así arranca solo

- **Decisión:** La contraseña no está en Git ni en ninguna capa. `.env` está en `.gitignore` y `.env.example` deja `DB_PASSWORD` vacío. Compose la inyecta al arrancar con `${DB_PASSWORD:?}`. En un Codespace nuevo, `postCreateCommand` corre una sola vez: copia el ejemplo y escribe una contraseña aleatoria en `.env`, que no se commitea. `postStartCommand` corre en cada arranque y hace `docker compose up -d --build --wait`.
- **Alternativas que evalué:**
  - `ENV DB_PASSWORD=…` en el Dockerfile. Pro: la imagen arranca sin archivo. Contra: el valor queda en una capa y `docker history` lo muestra. Es una fuga.
  - Un secreto de Codespaces. Pro: no está en el repo. Contra: el secreto es de quien crea el Codespace. Quien califica abre el repo con su cuenta y no tiene el mío, así que el stack no arranca.
  - Dejar `DB_PASSWORD` vacío en el ejemplo y pedir que alguien lo escriba a mano. Pro: no hay secreto en el repo. Contra: un Codespace nuevo no tiene `.env` y el criterio B3 exige que arranque solo.
- **Por qué elegí esta:** La contraseña de desarrollo se genera en el entorno, fuera de Git y fuera de la imagen. No es un secreto de producción: solo vive en ese Codespace para que Postgres acepte conexiones. En producción la credencial la pondría el entorno de despliegue, no el repositorio.
- **Fuentes consultadas:**
  - https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/
  - https://docs.docker.com/reference/compose-file/services/#env_file
  - https://docs.docker.com/reference/dockerfile/#env
  - https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-development-environment-secrets-for-your-repository-or-organization
  - https://containers.dev/implementors/json_reference/#lifecycle-scripts
- **Cómo lo verifiqué:** El historial de `.env` está vacío (solo está versionado `.env.example`):

```
git log --all --full-history -- .env
```

`docker history --no-trunc` de `libro-api:despues`, `libro-web:secreto` y `libro-db:secreto`, filtrado por `password`, `secret` y `DB_PASSWORD`, no devolvió ninguna capa.

- **Qué no me funcionó:** Confundir `env_file` con una capa de la imagen. Compose lee `.env` al crear el contenedor y mete `POSTGRES_PASSWORD` en el entorno del proceso. Eso no se escribe en el Dockerfile ni aparece en `docker history`. Si lo hubiera puesto en `ENV`, el secreto quedaría para siempre en la imagen.
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

En Codespaces, con `.env` ya creado (o con el secreto `DB_PASSWORD`), `.devcontainer/devcontainer.json` levanta el compose al abrir el entorno y abre el puerto 8080.

## Bitácora de decisiones

- **Tres servicios.** `web` sirve el HTML de la raíz, `api` corre gunicorn y `db` es Postgres 16. El HTML sigue en la raíz porque GitHub Pages lo necesita ahí; la imagen de nginx solo lo copia.
- **Mismo origen.** El navegador llama a `/api`. nginx reenvía esa ruta al servicio `api` usando `PORT` de `.env`. No hay URL ni puerto en `libro-de-visitas.js`.
- **Dos redes.** `frontal` une web y api. `datos` une api y db. Postgres no está en `frontal` ni tiene `ports`: desde el host no se alcanza.
- **Credenciales.** La contraseña vive solo en `.env` (gitignored) y entra a Postgres como `POSTGRES_PASSWORD` al arrancar. `.env.example` se commitea con `DB_PASSWORD` vacío. Los `.dockerignore` dejan `.env` fuera de las imágenes.
- **Datos.** El volumen `datos` guarda `/var/lib/postgresql/data`. `docker compose down` no lo borra; hace falta `docker compose down -v` para empezar de cero. Los SQL de `db/init/` corren solo con el volumen vacío.
- **Salud.** `db` usa `pg_isready`. `api` pide `GET /api/health`, que falla si no habla con la base. `web` pide ese mismo health a través del proxy. Cada uno espera al anterior con `condition: service_healthy`.
- **Proceso de la API.** La imagen usa `python:3.12-slim-bookworm`, instala dependencias como root y arranca gunicorn con el usuario `app`. El código de ejecución es el de la imagen (`/app`); `/workspace` es el repo montado para editar en Codespaces.
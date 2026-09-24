# Frontend estático. index.html sigue en la raíz del repo por GitHub Pages;
# aquí solo se copia dentro de la imagen. El puerto de la API llega por PORT.
FROM nginx:1.27-alpine

RUN apk add --no-cache curl

COPY web/nginx.conf /etc/nginx/templates/default.conf.template
COPY index.html estilos.css libro-de-visitas.js /usr/share/nginx/html/

EXPOSE 80

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1/ >/dev/null

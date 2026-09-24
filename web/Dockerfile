# Frontend estático. index.html sigue en la raíz del repo por GitHub Pages;
# aquí solo se copia dentro de la imagen. El puerto de la API llega por PORT.
# La imagen oficial arranca como root para poder escuchar en el puerto 80.
# Por debajo de 1024 hace falta ese privilegio. Aquí escucha en 8080 y corre como nginx.
FROM nginx:1.27-alpine

RUN apk add --no-cache curl \
    && sed -i 's|^user |#user |' /etc/nginx/nginx.conf \
    && sed -i 's|/var/run/nginx.pid|/tmp/nginx.pid|' /etc/nginx/nginx.conf \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d /usr/share/nginx/html

COPY --chown=nginx:nginx web/nginx.conf /etc/nginx/templates/default.conf.template
COPY --chown=nginx:nginx index.html estilos.css libro-de-visitas.js /usr/share/nginx/html/

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/ >/dev/null

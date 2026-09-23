"""Libro de visitas: API del LAB-02 en Python (Flask + psycopg).

Toda la configuración entra por variables de entorno. Aquí no hay ni una
contraseña ni un nombre de host escrito a mano, y así debe seguir.
"""
import os

import psycopg
from flask import Flask, jsonify, request
from psycopg.rows import dict_row

app = Flask(__name__)

DB = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": os.environ.get("DB_PORT", "5432"),
    "dbname": os.environ.get("DB_NAME", "libro"),
    "user": os.environ.get("DB_USER", "app"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "connect_timeout": 3,
}


def conectar():
    return psycopg.connect(**DB, row_factory=dict_row)


@app.get("/api/health")
def health():
    # "Estoy vivo" no alcanza: si no puedo hablar con la base, no estoy sano.
    try:
        with conectar() as con:
            con.execute("SELECT 1")
        return jsonify(status="ok")
    except psycopg.Error as e:
        return jsonify(status="error", detalle=str(e).strip()), 503


@app.get("/api/mensajes")
def listar():
    with conectar() as con:
        filas = con.execute(
            "SELECT id, nombre, mensaje, fecha FROM mensajes ORDER BY fecha DESC, id DESC LIMIT 100"
        ).fetchall()
    for f in filas:
        f["fecha"] = f["fecha"].isoformat()
    return jsonify(filas)


@app.post("/api/mensajes")
def crear():
    datos = request.get_json(silent=True) or {}
    nombre = str(datos.get("nombre", "")).strip()
    mensaje = str(datos.get("mensaje", "")).strip()

    if not nombre or not mensaje:
        return jsonify(error="Faltan el nombre o el mensaje."), 400
    if len(nombre) > 60:
        return jsonify(error="El nombre no puede pasar de 60 caracteres."), 400
    if len(mensaje) > 280:
        return jsonify(error="El mensaje no puede pasar de 280 caracteres."), 400

    with conectar() as con:
        fila = con.execute(
            # Parámetros, nunca concatenar texto del usuario dentro del SQL.
            "INSERT INTO mensajes (nombre, mensaje) VALUES (%s, %s) RETURNING id, nombre, mensaje, fecha",
            (nombre, mensaje),
        ).fetchone()
    fila["fecha"] = fila["fecha"].isoformat()
    return jsonify(fila), 201


if __name__ == "__main__":
    # Solo para probar a mano. En el contenedor se arranca con gunicorn.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "3000")))

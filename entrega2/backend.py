
"""Backend web para Nemotron 2 y SWI-Prolog."""

import os
import re
from uuid import uuid4

from flask import Flask, jsonify, request
from pyswip import Prolog

import chatbot_openrouter_nemotron2 as chatbot


app = Flask(__name__, static_folder="frontend", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 2048

prolog = Prolog()
prolog.consult(str(chatbot.ARCHIVO_KB))
indices = chatbot.crear_indice(prolog)

historiales = {}


@app.get("/")
def inicio():
    return app.send_static_file("index.html")


@app.get("/api/health")
def comprobar():
    cantidad = sum(len(v) for v in indices["pelicula"].values())
    return jsonify({"estado": "ok", "peliculas": cantidad})


@app.post("/api/chat")
def responder():
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({"error": "Se requiere un JSON válido."}), 400

    if set(datos) - {"pregunta", "sesion", "clave_api"}:
        return jsonify({"error": "Campos no permitidos."}), 400

    # La clave se recibe para esta petición, sin guardarla.
    clave = datos.get("clave_api")
    if (not isinstance(clave, str)
            or not 20 <= len(clave) <= 256
            or any(c.isspace() for c in clave)):
        return jsonify({"error": "Introduce una API Key válida."}), 400

    pregunta = datos.get("pregunta")
    if (not isinstance(pregunta, str)
            or not 1 <= len(pregunta.strip()) <= 400):
        return jsonify({"error": "Pregunta inválida."}), 400

    sesion = datos.get("sesion")
    if sesion is not None:
        if (not isinstance(sesion, str)
                or not re.fullmatch(r"[0-9a-f]{32}", sesion)):
            return jsonify({"error": "Sesión inválida."}), 400

    pregunta = pregunta.strip()
    sesion = sesion or uuid4().hex
    historial = historiales.get(sesion, [])

    try:
        generado, tiempo_llm, uso = chatbot.llamar_modelo(
            clave, pregunta, historial
        )

        plan = chatbot.validar_plan(generado, indices)
        tiempo_prolog = 0.0

        if plan["accion"] == "consulta":
            filas, truncado, tiempo_prolog, _ = (
                chatbot.consultar_prolog(prolog, plan)
            )
            respuesta = chatbot.presentar(
                filas, plan["campos"], truncado, plan["operacion"]
            )

        elif plan["accion"] == "aclarar":
            respuesta = plan["mensaje"]

        else:
            respuesta = "No entendí la pregunta."

    except RuntimeError as error:
        detalle = str(error)

        if "HTTP 401" in detalle or "HTTP 403" in detalle:
            return jsonify({
                "error": "API Key rechazada por OpenRouter."
            }), 401

        if "HTTP 429" in detalle:
            return jsonify({
                "error": "Límite de solicitudes de OpenRouter alcanzado."
            }), 429

        print("Error de OpenRouter:", type(error).__name__)
        return jsonify({
            "error": "No se pudo conectar con OpenRouter."
        }), 502

    except (ValueError, TypeError, KeyError) as error:
        print("Error de traducción:", type(error).__name__)
        return jsonify({
            "error": "No pude interpretar la consulta."
        }), 422

    except Exception as error:
        print("Error del backend:", type(error).__name__)
        return jsonify({
            "error": "No se pudo procesar la consulta."
        }), 502

    if sesion not in historiales and len(historiales) >= 100:
        historiales.pop(next(iter(historiales)))

    # Solo se almacenan preguntas y planes.
    # No guardamos la API Key ni respuestas de Prolog.
    historiales[sesion] = chatbot.guardar_historial(
        historial, pregunta, plan
    )

    return jsonify({
        "sesion": sesion,
        "respuesta": respuesta,
        "tiempo_llm": round(tiempo_llm, 2),
        "tiempo_prolog": round(tiempo_prolog, 4),
        "tokens_entrada": uso.get("prompt_tokens"),
        "tokens_salida": uso.get("completion_tokens"),
    })


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=8000,
        debug=False,
        threaded=False,
        use_reloader=False,
    )

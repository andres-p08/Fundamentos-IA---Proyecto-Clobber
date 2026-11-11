"""Chatbot híbrido: el LLM traduce preguntas y SWI-Prolog consulta la KB."""

import argparse
import getpass
import json
import os
import random
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


MODELO = "openai/gpt-oss-120b"
URL_API = "https://api.groq.com/openai/v1/chat/completions"
VARIABLE_CLAVE = "GROQ_API_KEY"
PROVEEDOR = "GroqCloud"
ARCHIVO_KB = Path(__file__).resolve().parent / "Chatbot_Prolog.pl"

CAMPOS = {
    "pelicula": "Pelicula", "anio": "Anio", "edad": "Edad",
    "duracion": "Duracion", "rating": "Rating", "genero": "Genero",
    "actor": "Actor", "director": "Director",
    "anio_actor": "NacimientoActor", "anio_director": "NacimientoDirector",
}
NUMERICOS = {"anio", "edad", "duracion", "rating", "anio_actor", "anio_director"}
REGLAS = {
    "pelicula_clasica", "pelicula_nueva", "pelicula_corta",
    "pelicula_larga", "buen_rating", "mal_rating",
    "restriccion_mayores_18", "apta_todo_publico", "es_comedia",
}
OPERADORES = {"eq": "=", "lt": "<", "le": "=<", "gt": ">", "ge": ">="}
ETIQUETAS = {
    "pelicula": "Película", "anio": "Año", "edad": "Edad mínima",
    "duracion": "Duración (min)", "rating": "Puntuación",
    "genero": "Género", "actor": "Actor", "director": "Director",
    "anio_actor": "Nacimiento del actor",
    "anio_director": "Nacimiento del director",
}

PROMPT = """Transforma preguntas de películas en un objeto JSON.
No tienes acceso a los hechos de la KB: no inventes resultados y no respondas
con conocimientos propios. SWI-Prolog resolverá las consultas.
Responde SOLO JSON, sin explicación ni bloques Markdown.

Formato: {"accion":"consulta","campos":["pelicula"],"filtros":[],"maximo_rating":false}
Si es ambiguo: {"accion":"aclarar","mensaje":"¿A cuál te refieres?"}
Si no se entiende: {"accion":"no_entendido"}

Campos: pelicula, anio, edad, duracion, rating, genero, actor, director,
anio_actor, anio_director.
Filtros: {"campo":"pelicula","op":"eq","valor":"nombre"}.
Operadores: eq (igual), lt (<), le (<=), gt (>), ge (>=).
Los campos de texto solo admiten eq. Usa números para valores numéricos.
Los nombres pueden venir con espacios: Python los resolverá contra la KB.
También puedes filtrar por:
- regla: una de pelicula_clasica, pelicula_nueva, pelicula_corta,
  pelicula_larga, buen_rating, mal_rating, restriccion_mayores_18,
  apta_todo_publico, es_comedia; solo op eq.
- director_de: película cuya dirección comparten las películas buscadas.
- actor_de: película con la que comparten un actor; solo op eq.

Usa maximo_rating=true para elegir solo películas de máxima puntuación
entre las que cumplan los filtros. Para preguntas de seguimiento, aprovecha
las consultas previas, pero solicita aclaración si el referente es ambiguo.
Si se menciona una película desconocida, traduce igual la consulta:
Prolog determina si existe. No asumas la respuesta.

Ejemplos:
¿Quién dirigió X y en qué año salió? ->
{"accion":"consulta","campos":["director","anio"],"filtros":[{"campo":"pelicula","op":"eq","valor":"X"}],"maximo_rating":false}
¿Qué películas son aptas para todo público? ->
{"accion":"consulta","campos":["pelicula"],"filtros":[{"campo":"regla","op":"eq","valor":"apta_todo_publico"}],"maximo_rating":false}
¿Qué comedias duran menos de 100 minutos? ->
{"accion":"consulta","campos":["pelicula"],"filtros":[{"campo":"genero","op":"eq","valor":"comedia"},{"campo":"duracion","op":"lt","valor":100}],"maximo_rating":false}
"""


def normalizar(texto):
    """Iguala nombres con/sin acentos, espacios, signos o guiones bajos."""
    texto = unicodedata.normalize("NFKD", str(texto).casefold())
    return "".join(c for c in texto if c.isascii() and c.isalnum())


def atomo_seguro(texto):
    """Restringe todo valor de texto a átomos Prolog sin código ejecutable."""
    if not isinstance(texto, str):
        raise ValueError("El valor de texto no es válido.")
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", "_", texto).strip("_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", texto):
        raise ValueError("No se pudo identificar el nombre solicitado.")
    return texto


def crear_indice(prolog):
    """Indexa nombres localmente una sola vez; nunca los envía al LLM."""
    consultas = {
        "pelicula": ("pelicula(Pelicula, _, _, _, _)", "Pelicula"),
        "actor": ("actor(Actor, _)", "Actor"),
        "director": ("director(Director, _)", "Director"),
    }
    indices = {}
    for categoria, (consulta, variable) in consultas.items():
        indice = {}
        for fila in prolog.query(consulta):
            valor = str(fila[variable])
            indice.setdefault(normalizar(valor), set()).add(valor)
        indices[categoria] = indice
    return indices


def validar_plan(plan, indices):
    """Comprueba que Nemotron/GPT-OSS solo solicite operaciones autorizadas."""
    if not isinstance(plan, dict):
        raise ValueError("La traducción no es un objeto JSON.")
    accion = plan.get("accion")
    if accion == "no_entendido":
        return {"accion": accion}
    if accion == "aclarar":
        return {"accion": accion, "mensaje": str(plan.get(
            "mensaje", "¿Puedes aclarar tu pregunta?"))[:180]}
    if accion != "consulta":
        raise ValueError("Operación no permitida.")

    campos = plan.get("campos")
    filtros = plan.get("filtros")
    if (not isinstance(campos, list) or not 1 <= len(campos) <= 6
            or any(c not in CAMPOS for c in campos)):
        raise ValueError("Campos de salida no permitidos.")
    if not isinstance(filtros, list) or len(filtros) > 8:
        raise ValueError("Filtros no permitidos.")

    validados = []
    for filtro in filtros:
        if not isinstance(filtro, dict):
            raise ValueError("Filtro incorrecto.")
        campo = filtro.get("campo")
        op = filtro.get("op")
        valor = filtro.get("valor")
        if campo not in set(CAMPOS) | {"regla", "director_de", "actor_de"}:
            raise ValueError("Campo de filtro desconocido.")
        if op not in OPERADORES:
            raise ValueError("Operador desconocido.")
        if campo == "regla":
            if op != "eq" or valor not in REGLAS:
                raise ValueError("Regla no autorizada.")
        elif campo in NUMERICOS:
            if (isinstance(valor, bool) or not isinstance(valor, (int, float))
                    or not -1000000 < valor < 1000000):
                raise ValueError("Filtro numérico inválido.")
        else:
            if op != "eq":
                raise ValueError("El filtro de texto requiere igualdad.")
            categoria = ("pelicula" if campo in {"director_de", "actor_de"}
                         else campo)
            atom = atomo_seguro(valor)
            if categoria in indices:
                coincidencias = indices[categoria].get(normalizar(valor), set())
                if len(coincidencias) > 1:
                    raise ValueError(f"Nombre ambiguo: {valor}.")
                if coincidencias:
                    atom = next(iter(coincidencias))
            valor = atom
        validados.append({"campo": campo, "op": op, "valor": valor})

    return {
        "accion": "consulta", "campos": list(dict.fromkeys(campos)),
        "filtros": validados,
        "maximo_rating": plan.get("maximo_rating") is True,
    }


def construir_consulta(plan):
    """Conecta los hechos y reglas existentes sin alterar la KB."""
    usados = set(plan["campos"]) | {f["campo"] for f in plan["filtros"]}
    if "director_de" in usados:
        usados.add("director")
    if "actor_de" in usados:
        usados.add("actor")
    metas = []
    for filtro in plan["filtros"]:
        campo, valor = filtro["campo"], filtro["valor"]
        if campo in CAMPOS and campo not in NUMERICOS:
            metas.append(f"{CAMPOS[campo]} = {valor}")
        elif campo == "director_de":
            metas.append(f"dirige(Director, {valor})")
        elif campo == "actor_de":
            metas.append(f"actua_en(Actor, {valor})")

    if "actor" in usados or "anio_actor" in usados:
        metas.append("actua_en(Actor, Pelicula)")
    if "director" in usados or "anio_director" in usados:
        metas.append("dirige(Director, Pelicula)")
    if "genero" in usados:
        metas.append("genero(Pelicula, Genero)")
    metas.append("pelicula(Pelicula, Anio, Edad, Duracion, Rating)")
    if "anio_actor" in usados:
        metas.append("actor(Actor, NacimientoActor)")
    if "anio_director" in usados:
        metas.append("director(Director, NacimientoDirector)")

    for filtro in plan["filtros"]:
        campo, op, valor = filtro["campo"], filtro["op"], filtro["valor"]
        if campo == "regla":
            metas.append(f"{valor}(Pelicula)")
        elif campo in NUMERICOS:
            metas.append(f"{CAMPOS[campo]} {OPERADORES[op]} {valor}")

    cuerpo = ", ".join(metas)
    if plan["maximo_rating"]:
        return (f"aggregate_all(max(Rating), ({cuerpo}), MaxRating), "
                f"({cuerpo}), Rating =:= MaxRating")
    return cuerpo


def consultar_prolog(prolog, plan):
    consulta = construir_consulta(plan)
    inicio = time.perf_counter()
    filas = list(prolog.query(consulta, maxresult=51))
    tiempo = time.perf_counter() - inicio
    resultado, vistos = [], set()
    for fila in filas:
        valores = tuple(str(fila[CAMPOS[c]]) for c in plan["campos"])
        if valores not in vistos:
            vistos.add(valores)
            resultado.append(valores)
    return resultado[:50], len(filas) > 50, tiempo, consulta


def presentar(filas, campos, truncado):
    if not filas:
        return "No se encontraron resultados en la base de conocimientos."
    salida = []
    for fila in filas:
        if len(fila) == 1:
            salida.append(f"- {fila[0].replace('_', ' ')}")
        else:
            salida.append("- " + " | ".join(
                f"{ETIQUETAS[c]}: {v.replace('_', ' ')}"
                for c, v in zip(campos, fila)))
    if truncado:
        salida.append("(Primeros 50 resultados; agrega filtros.)")
    return "\n".join(salida)


def llamar_modelo(clave, pregunta, historial):
    """Envía al modelo el esquema y la pregunta, nunca hechos de la KB."""
    texto = ("Historial de consultas (sin datos de la KB): "
             + json.dumps(historial[-3:], ensure_ascii=False)
             + "\nPregunta: " + pregunta)
    cuerpo = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": texto},
        ],
        **{"temperature": 0, "max_completion_tokens": 700,
         "reasoning_effort": "low", "include_reasoning": False,
         "response_format": {"type": "json_object"}},
    }
    solicitud = Request(
        URL_API, data=json.dumps(cuerpo, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {clave}",
                 "Content-Type": "application/json"},
        method="POST",
    )
    inicio = time.perf_counter()
    for intento in range(3):
        try:
            with urlopen(solicitud, timeout=60) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
            break
        except HTTPError as exc:
            detalle = exc.read().decode("utf-8", errors="replace")[:400]
            if exc.code in {408, 500, 502, 503, 504} and intento < 2:
                time.sleep(2 ** intento + random.uniform(0, 0.5))
                continue
            if exc.code == 429:
                aviso = exc.headers.get("Retry-After")
                detalle += f" (reintentar en {aviso} segundos)" if aviso else ""
            raise RuntimeError(f"{PROVEEDOR} HTTP {exc.code}: {detalle}") from exc
        except (URLError, TimeoutError) as exc:
            if intento < 2:
                time.sleep(2 ** intento + random.uniform(0, 0.5))
                continue
            raise RuntimeError(f"Sin conexión con {PROVEEDOR}.") from exc

    opciones = datos.get("choices") or []
    if not opciones:
        raise RuntimeError(f"{PROVEEDOR} no devolvió resultados.")
    contenido = opciones[0].get("message", {}).get("content") or ""
    if isinstance(contenido, list):
        contenido = "".join(p.get("text", "") for p in contenido
                            if isinstance(p, dict))
    contenido = re.sub(r"<think>.*?</think>", "", contenido, flags=re.S).strip()
    contenido = re.sub(r"^```(?:json)?\s*|\s*```$", "", contenido).strip()
    try:
        plan = json.loads(contenido)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{PROVEEDOR} no produjo JSON válido.") from exc
    return plan, time.perf_counter() - inicio, datos.get("usage") or {}


def main():
    parser = argparse.ArgumentParser(description="LLM + PySwip + SWI-Prolog")
    parser.add_argument("--check-kb", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if not ARCHIVO_KB.is_file():
        print(f"Falta {ARCHIVO_KB.name} junto al script.", file=sys.stderr)
        return 1
    try:
        from pyswip import Prolog
        prolog = Prolog()
        prolog.consult(str(ARCHIVO_KB))
        if not list(prolog.query("pelicula(_, _, _, _, _)", maxresult=1)):
            raise RuntimeError("No hay hechos pelicula/5.")
        indices = crear_indice(prolog)
    except Exception as exc:
        print(f"Error al cargar Prolog: {exc}", file=sys.stderr)
        return 1

    print(f"KB cargada mediante SWI-Prolog: {ARCHIVO_KB.name}.")
    if args.check_kb:
        cantidad = sum(len(v) for v in indices["pelicula"].values())
        print(f"Películas indexadas: {cantidad}.")
        print("Consulta Prolog correcta; no se utilizó el LLM.")
        return 0

    clave = os.getenv(VARIABLE_CLAVE, "").strip()
    if not clave:
        try:
            clave = getpass.getpass(f"Introduce {VARIABLE_CLAVE}: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelado.")
            return 1
    if not clave:
        print("No se introdujo una API Key.", file=sys.stderr)
        return 1

    print(f"Proveedor: {PROVEEDOR} | Modelo: {MODELO}")
    print("Escribe 'salir' para terminar.\n")
    historial = []
    while True:
        try:
            pregunta = input("Tú > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("Hasta luego.")
            break
        if not pregunta:
            continue
        try:
            generado, tiempo_llm, uso = llamar_modelo(clave, pregunta, historial)
            plan = validar_plan(generado, indices)
            if args.debug:
                print("Traducción:", json.dumps(plan, ensure_ascii=False))
            if plan["accion"] == "consulta":
                filas, truncado, tiempo_kb, consulta = consultar_prolog(prolog, plan)
                if args.debug:
                    print("Prolog:", consulta)
                print("\nChatbot > " + presentar(filas, plan["campos"], truncado))
                print(f"Tiempo LLM: {tiempo_llm:.2f}s | Prolog: {tiempo_kb:.4f}s")
                cantidad = len(filas)
            else:
                print("\nChatbot > " + plan.get("mensaje", "No entendí la pregunta."))
                print(f"Tiempo LLM: {tiempo_llm:.2f}s")
                cantidad = 0
            if uso:
                print(f"Tokens: {uso.get('prompt_tokens', '?')} entrada, "
                      f"{uso.get('completion_tokens', '?')} salida")
            print()
            historial.append({"pregunta": pregunta, "plan": plan,
                              "cantidad_resultados": cantidad})
            historial = historial[-3:]
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            print(f"\nError: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

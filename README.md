# Fundamentos-IA---Proyecto-Clobber
# Proyecto-Chatbot

## Chatbot LLM con Gemini
Chatbot de películas desarrollado en Python que utiliza Google Gemini mediante su API para responder preguntas en lenguaje natural, utilizando la base de conocimientos existente del Proyecto 2 (Chatbot_Prolog.pl).

**Requisitos**

* Python 3.14.
* Conexión a internet.
* API Key de Gemini.

Para obtener una API Key, ingresar a Google AI Studio (https://aistudio.google.com/) y acceder a la sección de claves de API.

**Ejecución**

Abrir una terminal desde la carpeta proyecto2_Arroyo_Frez_Peña_V y ejecutar:

1. Comprobar la base de conocimientos:

py -3.14 chatbot_gemini.py --check-kb

2. Ejecutar el chatbot:

py -3.14 chatbot_gemini.py

Al iniciar, el programa solicitará una API Key de Gemini. Cada usuario debe utilizar su propia clave.

**Funcionamiento**

* El modelo realiza la inferencia mediante la API de Gemini.
* Python lee la base de conocimientos existente y proporciona sus hechos y reglas como contexto al modelo.
* El programa no ejecuta SWI-Prolog ni realiza consultas Prolog.
* Las preguntas se realizan en lenguaje natural y las respuestas se generan mediante el LLM.
* El chatbot mantiene el contexto de la conversación durante su ejecución.

**Consideraciones**

* No requiere paquetes adicionales mediante pip; utiliza la biblioteca estándar de Python.
* Se necesita conexión a internet para comunicarse con Gemini.
* La API Key es privada y no debe publicarse ni incorporarse al repositorio.
* Las respuestas están condicionadas por la información disponible en la base de conocimientos.
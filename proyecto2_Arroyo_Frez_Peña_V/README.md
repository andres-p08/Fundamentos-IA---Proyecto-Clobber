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

## Chatbot LLM con NVIDIA Nemotron y OpenRouter

Chatbot de películas que utiliza NVIDIA Nemotron 3 Ultra mediante la API de OpenRouter.

**Modelo**: nvidia/nemotron-3-ultra-550b-a55b:free

**Obtener API Key**

Ingresar a OpenRouter y crear una clave de API. Cada usuario debe utilizar su propia clave.

**Ejecución**

Abrir una terminal desde la carpeta proyecto2_Arroyo_Frez_Peña_V y ejecutar:

1. Comprobar la base de conocimientos:

py -3.14 chatbot_openrouter_nemotron.py --check-kb

2. Ejecutar el chatbot:

py -3.14 chatbot_openrouter_nemotron.py

Al iniciar, el programa solicitará una API Key de OpenRouter si no está configurada como variable de entorno.

## Chatbot LLM con GPT-OSS 120B y GroqCloud

Chatbot de películas que utiliza GPT-OSS 120B mediante la API de GroqCloud.

**Modelo: openai/gpt-oss-120b**

**Obtener API Key**

Ingresar a GroqCloud y crear una clave de API. Cada usuario debe utilizar su propia clave.

**Ejecución**

Abrir una terminal desde la carpeta proyecto2_Arroyo_Frez_Peña_V y ejecutar:

1. Comprobar la base de conocimientos:

py -3.14 chatbot_groq_gpt_oss_120b.py --check-kb

2. Ejecutar el chatbot:

py -3.14 chatbot_groq_gpt_oss_120b.py

Al iniciar, el programa solicitará una API Key de Groq si no está configurada como variable de entorno.

**Funcionamiento**

* Python lee la base de conocimientos existente y proporciona sus hechos y reglas como contexto al modelo.
* La inferencia se realiza mediante la API del proveedor correspondiente.
* El programa no ejecuta SWI-Prolog ni realiza consultas Prolog.
* Las preguntas se realizan en lenguaje natural y las respuestas se generan mediante el LLM.
* Ambos chatbots mantienen el contexto de la conversación durante su ejecución.

**Consideraciones**

* No requieren paquetes adicionales mediante pip; utilizan la biblioteca estándar de Python.
* Se necesita conexión a internet para comunicarse con los proveedores.
* Las API Keys son privadas y no deben publicarse ni incorporarse al repositorio.
* Cada usuario debe generar su propia API Key.
* Nemotron utiliza la variante gratuita de OpenRouter, sujeta a disponibilidad y límites de uso.
* GPT-OSS 120B utiliza el plan gratuito de GroqCloud, sujeto a sus límites de solicitudes y tokens.
* Las respuestas están condicionadas por la información disponible en la base de conocimientos y pueden variar según el modelo utilizado.

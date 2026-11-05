# import llm // para cumplimiento de rúbrica
import spacy
import random
from pyswip import Prolog

class ChatbotPrologHibrido:
    def __init__(self, prolog_file="Chatbot_Prolog.pl"):
        # Cargar spaCy y PySwip
        self.nlp = spacy.load("es_core_news_md")
        self.prolog = Prolog()
        self.prolog.consult(prolog_file)

        # Estructuras para indexación dinámica desde Prolog
        self.entidades = {}       
        self.generos = set()
        
        # Mapeo de lemas a reglas declaradas 
        self.reglas_lemmas = {
            "esta": "actua_en",
            "estar": "actua_en",
            "bueno": "buen_rating",
            "buena": "buen_rating",
            "excelente": "buen_rating",
            "malo": "mal_rating",
            "corta": "pelicula_corta",
            "corto": "pelicula_corta",
            "larga": "pelicula_larga",
            "largo": "pelicula_larga",
            "clasico": "pelicula_clasica",
            "clasica": "pelicula_clasica",
            "nuevo": "pelicula_nueva",
            "nueva": "pelicula_nueva",
            "apta": "apta_todo_publico",
            "familiar": "apta_todo_publico"
        }

        # Cargar átomos dinámicamente al iniciar
        self._cargar_indice_dinamico()

    def _cargar_indice_dinamico(self):
        """Consulta PySwip para indexar automáticamente todos los datos del archivo"""
        # Indexar películas
        for res in self.prolog.query("pelicula(P, _, _, _, _)"):
            self.entidades[str(res["P"])] = "pelicula"

        # Indexar actores
        for res in self.prolog.query("actor(A, _)"):
            self.entidades[str(res["A"])] = "actor"

        # Indexar directores
        for res in self.prolog.query("director(D, _)"):
            self.entidades[str(res["D"])] = "director"

        # Indexar géneros
        for res in self.prolog.query("genero(_, G)"):
            g_str = str(res["G"])
            self.generos.add(g_str)
            self.entidades[g_str] = "genero"

    def _normalizar_texto(self, texto: str) -> str:
        """Convierte mayusculas a minusculas y los espacios a _"""
        return texto.lower().strip().replace(" ", "_")

    def _formatear_salida(self, atomo: str) -> str:
        """La inversa de la funcion anterior"""
        return str(atomo).replace("_", " ").title()

    def _extraer_entidades_usuario(self, tokens: list[str]) -> list[tuple[str, str]]:
        """Extrae entidades mediante n-gramas (3, 2 y 1 palabra) comparando con el índice dinámico."""
        entidades_encontradas = []
        n = len(tokens)
        
        for size in range(3, 0, -1):
            for i in range(n - size + 1):
                chunk = " ".join(tokens[i:i + size])
                candidate = self._normalizar_texto(chunk)
                if candidate in self.entidades:
                    tipo = self.entidades[candidate]
                    entidades_encontradas.append((candidate, tipo))
                    
        return entidades_encontradas

    def procesar_pregunta(self, texto_usuario: str) -> str:
        doc = self.nlp(texto_usuario)
        
        # Tokens y lemas procesados por spaCy
        tokens = [t.text.lower() for t in doc if not t.is_punct]
        lemmas = [t.lemma_.lower() for t in doc if not t.is_punct]

        # Extraer entidades de la pregunta comparando dinámicamente con la KB
        entidades = self._extraer_entidades_usuario(tokens)
        
        actores = [ent for ent, tipo in entidades if tipo == "actor"]
        directores = [ent for ent, tipo in entidades if tipo == "director"]
        peliculas = [ent for ent, tipo in entidades if tipo == "pelicula"]
        generos = [ent for ent, tipo in entidades if tipo == "genero"]

        # Desambiguación mediante intenciones (Verbos / Lemas con spaCy)

        # Consulta sobre un Actor 
        if actores:
            actor = actores[0]
            query = f"actua_en({actor}, Pelicula)"
            resultados = list(self.prolog.query(query))
            pelis = [self._formatear_salida(r["Pelicula"]) for r in resultados]
            return f"El actor {self._formatear_salida(actor)} actúa en: {', '.join(pelis)}."

        # Consulta sobre un Director 
        if directores:
            director = directores[0]
            query = f"dirige({director}, Pelicula)"
            resultados = list(self.prolog.query(query))
            pelis = [self._formatear_salida(r["Pelicula"]) for r in resultados]
            return f"El director {self._formatear_salida(director)} dirigió: {', '.join(pelis)}."

        # Detalle de una Película específica 
        if peliculas and ("actuar" in lemmas or "actua" in tokens or "actúa" in tokens or "actor" in lemmas or "quien" in lemmas or "quién" in tokens or "estar" in lemmas):
            peli = peliculas[0]
            query = f"actua_en(Actor, {peli})"
            resultados = list(self.prolog.query(query))
            
            if resultados:
                actores_lista = [self._formatear_salida(r["Actor"]) for r in resultados]
                return f"En la película '{self._formatear_salida(peli)}' actúa(n): {', '.join(actores_lista)}."
            return f"No tengo registrados los actores para la película '{self._formatear_salida(peli)}'."

        if peliculas and ("duracion" in tokens or "durar" in lemmas or "detalles" in tokens or "año" in tokens or "cuanto" in lemmas):
            peli = peliculas[0]
            query = f"pelicula({peli}, Anio, Restriccion, Duracion, Rating)"
            res = list(self.prolog.query(query))
            if res:
                info = res[0]
                return (f"Detalles de '{self._formatear_salida(peli)}': Año {info['Anio']}, "
                        f"Duración: {info['Duracion']} min, Rating: {info['Rating']}/10, "
                        f"Restricción edad: +{info['Restriccion']}.")

        # Caso 4: Consulta por Género 
        if generos:
            genero = generos[0]
            query = f"genero(Pelicula, {genero})"
            resultados = list(self.prolog.query(query))
            pelis = [self._formatear_salida(r["Pelicula"]) for r in resultados]
            return f"Películas del género '{genero}': {', '.join(pelis)}."

        # Caso 5: Reglas lógicas de Prolog mapeadas desde lemas de spaCy 
        for lemma in lemmas:
            if lemma in self.reglas_lemmas:
                regla = self.reglas_lemmas[lemma]
                query = f"{regla}(Pelicula)"
                resultados = list(self.prolog.query(query))
                pelis = [self._formatear_salida(r["Pelicula"]) for r in resultados]
                return f"Películas encontradas (Regla '{regla}'): {', '.join(pelis)}."

        # Caso 6. Reglas generales mapeadas por lemas 
        for lemma in lemmas:
            if lemma in self.reglas_lemmas:
                regla = self.reglas_lemmas[lemma]
                query = f"{regla}(Pelicula)"
                resultados = list(self.prolog.query(query))
                pelis = [self._formatear_salida(r["Pelicula"]) for r in resultados]
                return f"Películas encontradas (Regla '{regla}'): {', '.join(pelis)}."

        # Caso 7. Usuario pide recomendación de películas buenas / recomendadas
        if "bueno" in lemmas or "buena" in tokens or "recomendar" in lemmas or "recomendacion" in lemmas:
            query = "pelicula(Nombre, _, _, _, Rating), buen_rating(Nombre)"
            resultados = list(self.prolog.query(query))
            
            if resultados:
                # Si el usuario pide "una" película específica 
                if "una" in tokens or "un" in tokens:
                    seleccionada = random.choice(resultados)
                    nombre = self._formatear_salida(seleccionada["Nombre"])
                    rating = seleccionada["Rating"]
                    return f"Te recomiendo ver '{nombre}' (Rating: {rating}/10)."
                
                # Si pide varias o en general
                pelis = set(f"{self._formatear_salida(r['Nombre'])} ({r['Rating']}/10)" for r in resultados)
                return f"Películas recomendadas (Buen Rating >= 7):\n- " + "\n- ".join(pelis)

        return "No pude comprender la consulta. Intenta preguntar por un actor, director, género o características como 'buenas' o 'cortas'."


if __name__ == "__main__":
    bot = ChatbotPrologHibrido()
    print("==================================================")
    print(" Chatbot de Películas Activo (Escribe 'salir' para cerrar)")
    print("==================================================\n")

    while True:
        try:
            pregunta = input("Usuario > ")
            if pregunta.lower().strip() in ["salir", "exit", "quit"]:
                print("¡Hasta luego!")
                break
            
            if not pregunta.strip():
                continue

            respuesta = bot.procesar_pregunta(pregunta)
            print(f"Bot > {respuesta}\n")

        except (KeyboardInterrupt, EOFError):
            print("\n¡Hasta luego!")
            break

const formularioClave = document.getElementById("formulario-clave");
const campoClave = document.getElementById("clave");
const acceso = document.getElementById("acceso");
const chat = document.getElementById("chat");

const formulario = document.getElementById("formulario");
const pregunta = document.getElementById("pregunta");
const conversacion = document.getElementById("conversacion");
const estado = document.getElementById("estado");
const boton = document.getElementById("enviar");
const salir = document.getElementById("salir");

let claveApi = "";
let sesion = null;


function mostrarMensaje(autor, texto) {
    const mensaje = document.createElement("p");
    const nombre = document.createElement("strong");

    nombre.textContent = autor + ": ";
    mensaje.appendChild(nombre);
    mensaje.appendChild(document.createTextNode(texto));

    conversacion.appendChild(mensaje);
    conversacion.scrollTop = conversacion.scrollHeight;
}


formularioClave.addEventListener("submit", function(evento) {
    evento.preventDefault();

    claveApi = campoClave.value.trim();
    campoClave.value = "";

    if (!claveApi) return;

    acceso.hidden = true;
    chat.hidden = false;
    pregunta.focus();
});


salir.addEventListener("click", function() {
    claveApi = "";
    sesion = null;

    conversacion.replaceChildren();
    estado.textContent = "";
    pregunta.value = "";

    chat.hidden = true;
    acceso.hidden = false;
    campoClave.focus();
});


formulario.addEventListener("submit", async function(evento) {
    evento.preventDefault();

    const texto = pregunta.value.trim();

    if (!texto || boton.disabled) return;

    mostrarMensaje("Tú", texto);
    pregunta.value = "";
    boton.disabled = true;
    salir.disabled = true;
    estado.textContent = "Consultando...";

    try {
        const respuesta = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            cache: "no-store",
            body: JSON.stringify({
                pregunta: texto,
                sesion: sesion,
                clave_api: claveApi
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.error || "Error del servidor"
            );
        }

        sesion = datos.sesion;
        mostrarMensaje("Chatbot", datos.respuesta);

        estado.textContent =
            "LLM: " + datos.tiempo_llm + "s | " +
            "Prolog: " + datos.tiempo_prolog + "s | " +
            "Tokens: " + datos.tokens_entrada +
            " / " + datos.tokens_salida;

    } catch (error) {
        mostrarMensaje("Sistema", error.message);
        estado.textContent = "Error en la consulta";

    } finally {
        boton.disabled = false;
        salir.disabled = false;
        pregunta.focus();
    }
});

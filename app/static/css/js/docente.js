document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.querySelector("#tabla-solicitudes");
    const contador = document.querySelector("#contador-pendientes");
    const historial = document.querySelector("#historial-decisiones");
    const mensaje = document.querySelector("#mensaje-solicitud");

    // Si la página no contiene la tabla de solicitudes, no hace nada.
    if (!tabla) {
        return;
    }

    // Muestra mensajes en la página.
    function mostrarMensaje(texto) {
        if (!mensaje) {
            return;
        }

        mensaje.textContent = texto;
        mensaje.className = "mensaje-demo";

        // El mensaje desaparece después de 4 segundos.
        window.setTimeout(() => {
            mensaje.textContent = "";
            mensaje.className = "";
        }, 4000);
    }

    // Actualiza el número de solicitudes que siguen pendientes.
    function actualizarContador() {
        if (!contador) {
            return;
        }

        const filas = tabla.querySelectorAll("tbody tr");

        let pendientes = 0;

        filas.forEach((fila) => {
            const estado = fila.querySelector(".estado");

            if (
                estado &&
                estado.textContent.trim().toLowerCase() === "pendiente"
            ) {
                pendientes++;
            }
        });

        contador.textContent = `${pendientes} pendiente${pendientes !== 1 ? "s" : ""}`;
        contador.className = pendientes > 0
            ? "estado estado-pendiente"
            : "estado estado-activo";
    }

    // Añade cada decisión al historial visible.
    function agregarAlHistorial(estudiante, decision) {
        if (!historial) {
            return;
        }

        // Quita el mensaje inicial si todavía aparece.
        const mensajeInicial = historial.querySelector(".texto-ayuda");

        if (mensajeInicial) {
            mensajeInicial.remove();
        }

        const registro = document.createElement("p");
        const fecha = new Date().toLocaleString("es-CO");

        registro.textContent =
            `${fecha} — ${estudiante}: solicitud ${decision.toLowerCase()}.`;

        historial.prepend(registro);
    }

    // Gestiona los botones Aprobar y Rechazar.
    tabla.addEventListener("click", (evento) => {
        const boton = evento.target.closest("[data-accion]");

        if (!boton) {
            return;
        }

        const accion = boton.dataset.accion;

        if (accion !== "aprobar" && accion !== "rechazar") {
            return;
        }

        const fila = boton.closest("tr");

        if (!fila) {
            return;
        }

        const estado = fila.querySelector(".estado");

        if (!estado) {
            return;
        }

        // Evita procesar una solicitud más de una vez.
        if (estado.textContent.trim().toLowerCase() !== "pendiente") {
            mostrarMensaje("Esta solicitud ya fue procesada.");
            return;
        }

        const celdas = fila.querySelectorAll("td");
        const estudiante = celdas[0]?.textContent.trim() || "Estudiante";
        const decision = accion === "aprobar" ? "Aprobada" : "Rechazada";

        const confirmacion = window.confirm(
            `¿Deseas ${accion} la solicitud de ${estudiante}?`
        );

        if (!confirmacion) {
            return;
        }

        // Actualiza el estado visual de la solicitud.
        estado.textContent = decision;
        estado.className = accion === "aprobar"
            ? "estado estado-activo"
            : "estado estado-rechazado";

        // Actualiza la última columna de la tabla.
        const celdaDecision = celdas[celdas.length - 1];

        if (celdaDecision) {
            celdaDecision.textContent = `${decision} en esta sesión`;
        }

        // Desactiva los botones para impedir otra decisión.
        fila.querySelectorAll("[data-accion]").forEach((botonFila) => {
            botonFila.disabled = true;
        });

        // Actualiza contador, historial y mensaje.
        actualizarContador();
        agregarAlHistorial(estudiante, decision);
        mostrarMensaje(
            `La solicitud de ${estudiante} fue ${decision.toLowerCase()} correctamente.`
        );
    });

    // Evita que los enlaces de demostración con href="#" recarguen la página.
    document.querySelectorAll('a[href="#"]').forEach((enlace) => {
        enlace.addEventListener("click", (evento) => {
            evento.preventDefault();
        });
    });

    // Gestiona formularios de demostración sin enviar datos al servidor.
    document.querySelectorAll("form[data-demo='true']").forEach((formulario) => {
        formulario.addEventListener("submit", (evento) => {
            evento.preventDefault();

            if (!formulario.reportValidity()) {
                return;
            }

            mostrarMensaje("Los cambios se simularon correctamente en pantalla.");
        });
    });

    // Limpia formularios de demostración cuando exista un botón para ello.
    document.querySelectorAll("[data-accion='limpiar']").forEach((boton) => {
        boton.addEventListener("click", () => {
            const formulario = boton.closest("form");

            if (formulario) {
                formulario.reset();
                mostrarMensaje("Se limpiaron los campos del formulario.");
            }
        });
    });

    // Calcula el contador al abrir la página.
    actualizarContador();
});

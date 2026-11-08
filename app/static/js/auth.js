
document.addEventListener("DOMContentLoaded", function () {
    const formLogin = document.getElementById("formLogin");
    const formRegistro = document.getElementById("formRegistro");

    // ENVIO DE FORMULARIOS
    async function enviarFormulario(url, datos, mensaje) {
        mensaje.textContent = "Procesando...";

        try {
            const respuesta = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(datos)
            });

            const texto = await respuesta.text();

            console.log("RESPUESTA DEL SERVIDOR:", texto);

            let resultado;

            try {
                resultado = JSON.parse(texto);
            } catch {
                throw new Error(
                    "El servidor devolvió una página HTML. Revisa la consola y los registros de Flask."
                );
            }

            if (!respuesta.ok) {
                throw new Error(
                    resultado.mensaje || "No fue posible completar la solicitud."
                );
            }

            mensaje.textContent = resultado.mensaje || "Operación completada.";

            if (resultado.redirect) {
                window.location.href = resultado.redirect;
            }

        } catch (error) {
            console.error("ERROR:", error);

            mensaje.textContent = error.message ||
                "No fue posible conectar con el servidor.";
        }
    }

    // INICIO DE SESION
    formLogin?.addEventListener("submit", async function (evento) {
        evento.preventDefault();

        if (!formLogin.reportValidity()) return;

        const correo = document.getElementById("correo").value.trim();
        const contrasena = document.getElementById("contrasena").value;
        const mensaje = document.getElementById("mensajeLogin");

        await enviarFormulario("/api/login", {
            correo: correo,
            contrasena: contrasena
        }, mensaje);
    });

    // ELEMENTOS DEL REGISTRO
    const rolRegistro = document.getElementById("rol");
    const facultadRegistro = document.getElementById("facultad");
    const programaRegistro = document.getElementById("programa");
    const campoPrograma = document.getElementById("campoPrograma");

    // FILTRAR PROGRAMAS POR FACULTAD
    function actualizarProgramas() {
        if (!programaRegistro || !facultadRegistro) return;

        const idFacultad = facultadRegistro.value;

        Array.from(programaRegistro.options).forEach(opcion => {
            if (!opcion.value) return;

            opcion.hidden = opcion.dataset.facultad !== idFacultad;
        });

        programaRegistro.value = "";
    }

    // MOSTRAR PROGRAMA SOLO PARA ESTUDIANTES
    rolRegistro?.addEventListener("change", function () {
        if (campoPrograma) {
            campoPrograma.hidden = rolRegistro.value !== "ESTUDIANTE";
        }

        if (programaRegistro) {
            programaRegistro.required = rolRegistro.value === "ESTUDIANTE";
        }
    });

    // ACTUALIZAR PROGRAMAS AL CAMBIAR FACULTAD
    facultadRegistro?.addEventListener("change", actualizarProgramas);

    // REGISTRO
    formRegistro?.addEventListener("submit", async function (evento) {
        evento.preventDefault();

        if (!formRegistro.reportValidity()) return;

        const contrasena = document.getElementById("claveRegistro").value;
        const confirmar = document.getElementById("confirmarClave").value;
        const correo = document.getElementById("correoRegistro").value.trim();
        const rol = rolRegistro.value;
        const mensaje = document.getElementById("mensajeRegistro");

        // VALIDAR CORREO
        if (!correo.toLowerCase().endsWith("@unilibre.edu.co")) {
            mensaje.textContent = "Debes utilizar tu correo institucional.";
            return;
        }

        // VALIDAR CONTRASEÑAS
        if (contrasena !== confirmar) {
            mensaje.textContent = "Las contraseñas no coinciden.";
            return;
        }

        if (contrasena.length < 8) {
            mensaje.textContent = "La contraseña debe tener al menos 8 caracteres.";
            return;
        }

        // ENVIAR SOLICITUD
        await enviarFormulario("/api/registro", {
            nombres: document.getElementById("nombres").value.trim(),
            apellidos: document.getElementById("apellidos").value.trim(),
            documento: document.getElementById("documento").value.trim(),
            fecha_nacimiento: document.getElementById("fechaNacimiento").value,
            correo: correo,
            rol: rol,
            id_facultad: facultadRegistro.value,
            id_programa: rol === "ESTUDIANTE"
                ? programaRegistro.value
                : null,
            contrasena: contrasena
        }, mensaje);
    });

});

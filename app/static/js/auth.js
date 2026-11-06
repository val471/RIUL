
document.addEventListener("DOMContentLoaded", function () {
    const formLogin = document.getElementById("formLogin");
    const formRegistro = document.getElementById("formRegistro");

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

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(resultado.mensaje || "No fue posible completar la solicitud.");
            }

            mensaje.textContent = resultado.mensaje || "Operación completada.";

            if (resultado.redirect) {
                window.location.href = resultado.redirect;
            }
        } catch (error) {
            mensaje.textContent = error.message ||
                "No fue posible conectar con el servidor.";
        }
    }

    // Inicio de sesión
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

    // Registro
    formRegistro?.addEventListener("submit", async function (evento) {
        evento.preventDefault();

        if (!formRegistro.reportValidity()) return;

        const contrasena = document.getElementById("claveRegistro").value;
        const confirmar = document.getElementById("confirmarClave").value;
        const correo = document.getElementById("correoRegistro").value.trim();
        const mensaje = document.getElementById("mensajeRegistro");

        if (contrasena !== confirmar) {
            mensaje.textContent = "Las contraseñas no coinciden.";
            return;
        }

        if (contrasena.length < 8) {
            mensaje.textContent = "La contraseña debe tener al menos 8 caracteres.";
            return;
        }

        await enviarFormulario("/api/registro", {
            nombres: document.getElementById("nombres").value.trim(),
            apellidos: document.getElementById("apellidos").value.trim(),
            documento: document.getElementById("documento").value.trim(),
            correo: correo,
            rol: document.getElementById("rol").value,
            facultad: document.getElementById("facultad").value,
            contrasena: contrasena
        }, mensaje);
    });
});

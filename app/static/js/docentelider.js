
document.addEventListener("DOMContentLoaded", () => {

    // ========================================
    // ELEMENTOS PRINCIPALES
    // ========================================

    const sidebar = document.getElementById("sidebar");
    const tituloModulo = document.getElementById("tituloModulo");
    const enlacesMenu = document.querySelectorAll(".menu a[data-modulo]");
    const modulos = document.querySelectorAll(".contenido .modulo");


    function sesionVencida(respuesta) {
        if (respuesta.redirected && respuesta.url.includes("/iniciar-sesion")) {
            window.location.href = "/iniciar-sesion";
            return true;
        }
        return false;
    }

    // ========================================
    // ICONOS SVG
    // ========================================

    const ICONOS = {
        home: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
        user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/>',
        shield: '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>',
        users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        clipboard: '<rect x="5" y="4" width="14" height="18" rx="2"/><path d="M9 4V2h6v2"/><path d="M9 12h6M9 16h6"/>',
        folder: '<path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
        mega: '<path d="m3 11 18-5v12L3 13z"/><path d="M11.6 15.8 13 21H9l-2-6"/><path d="M21 10a2 2 0 0 1 0 4"/>',
        cal: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>',
        check: '<path d="m5 12 4 4L19 6"/>',
        book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        chart: '<path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-5 5"/>',
        bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/>',
        out: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>'
    };

    // INSERTAR ICONOS

    document.querySelectorAll("[data-icon]").forEach(element => {

        const nombreIcono = element.dataset.icon;

        if (ICONOS[nombreIcono] && !element.querySelector(".menu-icono")) {

            const contenedorIcono = document.createElement("span");

            contenedorIcono.className = "menu-icono";

            contenedorIcono.innerHTML = `
                <svg viewBox="0 0 24 24"
                     width="20"
                     height="20"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="1.8"
                     stroke-linecap="round"
                     stroke-linejoin="round"
                     aria-hidden="true">
                    ${ICONOS[nombreIcono]}
                </svg>
            `;

            element.prepend(contenedorIcono);
        }
    });

    // ========================================
    // TITULOS DE LOS MODULOS
    // ========================================

    const titulos = {
        inicio: "Inicio",
        perfil: "Mi perfil",
        semilleros: "Semilleros",
        usuarios: "Usuario",
        solicitudes: "Solicitudes",
        proyectos: "Proyectos",
        convocatorias: "Convocatorias",
        eventos: "Eventos",
        logros: "Logros",
        publicaciones: "Publicaciones",
        ranking: "Ranking"
    };


        // ========================================
    // IDENTIDAD (AVATAR Y NOMBRE EN EL MENU)
    // ========================================

    let datosPerfil = {};

    function obtenerIniciales(nombre) {

        return (nombre || "DL")
            .trim()
            .split(/\s+/)
            .slice(0, 2)
            .map(palabra => palabra.charAt(0))
            .join("")
            .toUpperCase();
    }

    function pintarAvatar(elemento, datos) {

        if (!elemento) {
            return;
        }

        if (datos.foto_perfil) {

            const imagen = document.createElement("img");

            imagen.src = datos.foto_perfil;
            imagen.alt = "Foto de perfil";
            imagen.style.cssText =
                "width:100%;height:100%;object-fit:cover;border-radius:50%";

            elemento.replaceChildren(imagen);

        } else {

            elemento.textContent = obtenerIniciales(datos.nombre_institucional);
        }
    }

    function aplicarIdentidad(datos) {

        pintarAvatar(document.getElementById("avatarIniciales"), datos);
        pintarAvatar(document.getElementById("avatarEncabezado"), datos);

        const nombreLateral = document.getElementById("nombreLateral");
        const nombreSaludo = document.getElementById("nombreSaludo");

        if (nombreLateral && datos.nombre_institucional) {
            nombreLateral.textContent = datos.nombre_institucional;
        }

        if (nombreSaludo && datos.nombre_institucional) {
            nombreSaludo.textContent = datos.nombre_institucional.split(/\s+/)[0];
        }
    }

    async function consultarPerfil() {

        const respuesta = await fetch("/docentelider/api/perfil");
        
        

        if (!respuesta.ok) {
            throw new Error("No se pudieron consultar los datos");
        }

        datosPerfil = await respuesta.json();

        aplicarIdentidad(datosPerfil);

        return datosPerfil;
    }

    function mostrarMensajePerfil(id, texto, tipo) {

        const elemento = document.getElementById(id);

        if (!elemento) {
            return;
        }

        elemento.textContent = texto;
        elemento.className = "perfil-mensaje " + (tipo || "exito");
        elemento.hidden = false;
    }

    async function enviarJSON(url, datos) {

        const respuesta = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json().catch(() => ({}));

        return {
            ok: respuesta.ok,
            mensaje: resultado.mensaje || "No fue posible completar la acción."
        };
    }

    function solicitudPendiente(campo) {

        const solicitud = datosPerfil.solicitudes?.[campo];

        return (solicitud?.estado || "").toUpperCase() === "PENDIENTE";
    }

    // ========================================
    // CARGAR HTML DE MI PERFIL
    // ========================================

    let perfilCargado = false;

    async function cargarHTMLPerfil() {

        const contenedorPerfil = document.getElementById("perfil");

        if (!contenedorPerfil || perfilCargado) {
            return;
        }

        try {

            contenedorPerfil.innerHTML = "<p>Cargando perfil...</p>";

            const respuesta = await fetch("/docentelider/perfil");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("No se pudo cargar el HTML del perfil");
            }

            const html = await respuesta.text();

            contenedorPerfil.innerHTML = html;
            perfilCargado = true;

            await cargarDatosPerfil();

            configurarFotoPerfil();
            configurarPerfil();

        } catch (error) {

            console.error("Error al cargar el perfil:", error);

            contenedorPerfil.innerHTML = `
                <p>No se pudo cargar el perfil.</p>
            `;
        }
    }

        // ========================================
    // CARGAR DATOS DEL PERFIL
    // ========================================

    function mostrarEstadoSolicitud(id, solicitud) {

        const elemento = document.getElementById(id);

        if (!elemento) {
            return;
        }

        if (!solicitud) {
            elemento.hidden = true;
            return;
        }

        const estado = (solicitud.estado || "").toUpperCase();
        let texto = "";

        if (estado === "PENDIENTE") {
            texto = "Pendiente de aprobación: «" + solicitud.valor_nuevo + "»";
        } else if (estado === "APROBADA") {
            texto = "Último cambio aprobado";
        } else if (estado === "RECHAZADA") {
            texto = "Cambio rechazado, se conservan tus datos anteriores";

            if (solicitud.motivo_rechazo) {
                texto += ". Motivo: " + solicitud.motivo_rechazo;
            }
        }

        elemento.textContent = texto;
        elemento.className = "perfil-estado " + estado.toLowerCase();
        elemento.hidden = !texto;
    }

    async function cargarDatosPerfil() {

        try {

            const datos = await consultarPerfil();

            const nombre = document.getElementById("nombrePerfil");
            const correo = document.getElementById("correoPerfil");
            const facultad = document.getElementById("facultadPerfil");

            if (nombre) nombre.value = datos.nombre_institucional || "";
            if (correo) correo.value = datos.correo_institucional || "";
            if (facultad) facultad.value = datos.facultad || "";

            pintarAvatar(document.getElementById("fotoPerfil"), datos);

            mostrarEstadoSolicitud(
                "estadoNombre",
                datos.solicitudes?.nombre_institucional
            );

            mostrarEstadoSolicitud(
                "estadoCorreo",
                datos.solicitudes?.correo_institucional
            );

        } catch (error) {

            console.error("Error al cargar los datos del perfil:", error);
        }
    }

    // ========================================
    // CAMBIAR FOTO DE PERFIL
    // ========================================

    function configurarFotoPerfil() {

        const nuevaFoto = document.getElementById("nuevaFoto");

        if (!nuevaFoto) {
            return;
        }

        nuevaFoto.addEventListener("change", async () => {

            const archivo = nuevaFoto.files[0];

            if (!archivo) {
                return;
            }

            const tiposPermitidos = ["image/png", "image/jpeg", "image/webp"];

            if (!tiposPermitidos.includes(archivo.type)) {

                mostrarMensajePerfil(
                    "mensajePerfil",
                    "Formato no permitido. Usa PNG, JPG o WEBP.",
                    "error"
                );

                nuevaFoto.value = "";
                return;
            }

            if (archivo.size > 2 * 1024 * 1024) {

                mostrarMensajePerfil(
                    "mensajePerfil",
                    "La imagen no debe superar 2 MB.",
                    "error"
                );

                nuevaFoto.value = "";
                return;
            }

            const formulario = new FormData();
            formulario.append("foto", archivo);

            try {

                const respuesta = await fetch("/docentelider/api/perfil/foto", {
                    method: "POST",
                    body: formulario
                });

                const resultado = await respuesta.json().catch(() => ({}));

                if (!respuesta.ok) {
                    throw new Error(
                        resultado.mensaje || "No se pudo actualizar la foto."
                    );
                }

                datosPerfil.foto_perfil = resultado.foto_perfil;

                pintarAvatar(document.getElementById("fotoPerfil"), datosPerfil);
                aplicarIdentidad(datosPerfil);

                mostrarMensajePerfil("mensajePerfil", resultado.mensaje, "exito");

            } catch (error) {

                mostrarMensajePerfil("mensajePerfil", error.message, "error");

            } finally {

                nuevaFoto.value = "";
            }
        });
    }

    // ========================================
    // EDITAR DATOS Y CAMBIAR CONTRASEÑA
    // ========================================

    function configurarPerfil() {

        const formulario = document.getElementById("formPerfilDocente");
        const nombre = document.getElementById("nombrePerfil");
        const correo = document.getElementById("correoPerfil");
        const btnEditar = document.getElementById("btnEditarPerfil");
        const btnCancelar = document.getElementById("btnCancelarPerfil");
        const btnEnviar = document.getElementById("guardarPerfil");
        const formClave = document.getElementById("formContrasena");

        if (!formulario || !nombre || !correo) {
            return;
        }

        function modoEdicion(activo) {

            const nombrePendiente = solicitudPendiente("nombre_institucional");
            const correoPendiente = solicitudPendiente("correo_institucional");

            nombre.readOnly = !activo || nombrePendiente;
            correo.readOnly = !activo || correoPendiente;

            btnEditar.hidden = activo;
            btnCancelar.hidden = !activo;
            btnEnviar.hidden = !activo;

            btnEditar.disabled = nombrePendiente && correoPendiente;
        }

        btnEditar.addEventListener("click", () => {

            document.getElementById("mensajePerfil").hidden = true;

            modoEdicion(true);

            (nombre.readOnly ? correo : nombre).focus();
        });

        btnCancelar.addEventListener("click", () => {

            nombre.value = datosPerfil.nombre_institucional || "";
            correo.value = datosPerfil.correo_institucional || "";

            modoEdicion(false);
        });

        formulario.addEventListener("submit", async event => {

            event.preventDefault();

            const cambios = {};

            if (!nombre.readOnly &&
                nombre.value.trim() !== datosPerfil.nombre_institucional) {
                cambios.nombre = nombre.value.trim();
            }

            if (!correo.readOnly &&
                correo.value.trim().toLowerCase() !== datosPerfil.correo_institucional) {
                cambios.correo = correo.value.trim().toLowerCase();
            }

            if (!Object.keys(cambios).length) {

                mostrarMensajePerfil(
                    "mensajePerfil",
                    "No hiciste ningún cambio en tus datos.",
                    "error"
                );

                return;
            }

            btnEnviar.disabled = true;

            const resultado = await enviarJSON(
                "/docentelider/api/perfil/solicitud",
                cambios
            );

            btnEnviar.disabled = false;

            mostrarMensajePerfil(
                "mensajePerfil",
                resultado.mensaje,
                resultado.ok ? "exito" : "error"
            );

            if (resultado.ok) {
                await cargarDatosPerfil();
                modoEdicion(false);
            }
        });

        // CAMBIAR CONTRASEÑA

        formClave?.addEventListener("submit", async event => {

            event.preventDefault();

            const actual = document.getElementById("contrasenaActual").value;
            const nueva = document.getElementById("contrasenaNueva").value;
            const confirmar = document.getElementById("contrasenaConfirmar").value;

            if (nueva.length < 8) {

                mostrarMensajePerfil(
                    "mensajeClave",
                    "La nueva contraseña debe tener mínimo 8 caracteres.",
                    "error"
                );

                return;
            }

            if (nueva !== confirmar) {

                mostrarMensajePerfil(
                    "mensajeClave",
                    "La confirmación no coincide con la nueva contraseña.",
                    "error"
                );

                return;
            }

            const boton = formClave.querySelector("button[type='submit']");

            boton.disabled = true;

            const resultado = await enviarJSON(
                "/docentelider/api/perfil/contrasena",
                { actual, nueva, confirmar }
            );

            boton.disabled = false;

            mostrarMensajePerfil(
                "mensajeClave",
                resultado.mensaje,
                resultado.ok ? "exito" : "error"
            );

            if (resultado.ok) {
                formClave.reset();
            }
        });

        modoEdicion(false);
    }

    // ========================================
    // CARGAR HTML DE SEMILLEROS
    // ========================================

    let semillerosHTMLCargado = false;

    async function cargarHTMLSemilleros() {

        const contenedor = document.getElementById("semilleros");

        if (!contenedor || semillerosHTMLCargado) {
            return;
        }

        try {

            contenedor.innerHTML = "<p>Cargando semilleros...</p>";

            const respuesta = await fetch("/docentelider/semilleros");
            
            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("No se pudo cargar el modulo de semilleros");
            }

            const html = await respuesta.text();

            contenedor.innerHTML = html;
            semillerosHTMLCargado = true;

            configurarModuloSemilleros();

        } catch (error) {

            console.error("Error al cargar semilleros:", error);

            contenedor.innerHTML = `
                <p>No se pudo cargar el modulo de semilleros.</p>
            `;
        }
    }


        // ========================================
    // CARGAR HTML DEL RESTO DE MODULOS
    // ========================================

    const RUTAS_MODULOS = {
        usuarios: "/docentelider/usuario",
        solicitudes: "/docentelider/solicitudes",
        proyectos: "/docentelider/proyectos",
        convocatorias: "/docentelider/convocatorias",
        eventos: "/docentelider/eventos",
        logros: "/docentelider/logros",
        publicaciones: "/docentelider/publicaciones",
        ranking: "/docentelider/ranking"
    };

    const modulosCargados = {};

    async function cargarHTMLModulo(id) {

        const contenedor = document.getElementById(id);

        if (!contenedor || modulosCargados[id]) {
            return;
        }

        try {

            contenedor.innerHTML = "<p>Cargando...</p>";

            const respuesta = await fetch(RUTAS_MODULOS[id]);

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            contenedor.innerHTML = await respuesta.text();
            modulosCargados[id] = true;

        } catch (error) {

            console.error("Error al cargar el modulo " + id + ":", error);

            contenedor.innerHTML = `<p>No se pudo cargar el modulo (${RUTAS_MODULOS[id]}): ${error.message}</p>`;
        }
    }

    // ========================================
    // MODULO PROYECTOS
    // ========================================

    function configurarModuloProyectos() {

        const tablaProyectos = document.getElementById("tablaProyectos");

        if (!tablaProyectos) {
            return;
        }

        const filas = tablaProyectos.querySelectorAll("tr[data-proyecto]");

        const total = document.getElementById("totalProyectos");
        const activos = document.getElementById("proyectosActivos");
        const revision = document.getElementById("proyectosRevision");

        if (total) {
            total.textContent = filas.length;
        }

        if (activos) {
            activos.textContent = tablaProyectos.querySelectorAll(
                '[data-estado="Activo"]'
            ).length;
        }

        if (revision) {
            revision.textContent = tablaProyectos.querySelectorAll(
                '[data-estado="En revisión"]'
            ).length;
        }
    }

    // ========================================
    // MODULO DE MI SEMILLERO
    // ========================================

    let semillerosConfigurados = false;
        async function configurarModuloSemilleros() {

        const contenedor = document.getElementById("contenido-semilleros");

        if (!contenedor || semillerosConfigurados) {
            return;
        }

        const btnEditar = contenedor.querySelector("#btnEditarSemillero");
        const estadoVacio = contenedor.querySelector("#estadoVacioSemilleros");
        const detalleSemillero = contenedor.querySelector("#detalleMiSemillero");

        if (!estadoVacio || !detalleSemillero) {
            return;
        }

        semillerosConfigurados = true;

        btnEditar?.addEventListener("click", () => {

            document.dispatchEvent(
                new CustomEvent("editarInformacionSemillero")
            );

        });

        await cargarMiSemillero(contenedor, estadoVacio, detalleSemillero);
    }

    async function cargarMiSemillero(contenedor, estadoVacio, detalle) {

        const poner = (id, valor) => {
            const elemento = contenedor.querySelector("#" + id);
            if (elemento) {
                elemento.textContent = valor;
            }
        };

        try {

            const respuesta = await fetch("/docentelider/api/semillero");

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const s = await respuesta.json();

            if (!s.asignado) {
                estadoVacio.style.display = "";
                detalle.hidden = true;
                return;
            }

            poner("nombreMiSemillero", s.nombre);
            poner("totalIntegrantesSemillero", s.integrantes);
            poner("totalProyectosSemillero", s.proyectos);
            poner("estadoMiSemillero", s.estado);

            poner("detalleNombreSemillero", s.nombre);
            poner("detalleFacultadSemillero", s.facultad);
            poner("detalleLineaSemillero", s.linea || "No registrada");
            poner("detalleDescripcionSemillero", s.descripcion || "Sin descripción");

            estadoVacio.style.display = "none";
            detalle.hidden = false;

        } catch (error) {

            console.error("Error al cargar mi semillero:", error);
        }
    }


    
    // ========================================
    // MODULO USUARIO
    // ========================================

    function configurarModuloUsuario() {

        const buscarIntegrante = document.getElementById("buscarIntegrante");
        const filtroRol = document.getElementById("filtroRol");
        const tablaIntegrantes = document.getElementById("tablaIntegrantes");
        const totalIntegrantes = document.getElementById("totalIntegrantes");

        if (!tablaIntegrantes || tablaIntegrantes.dataset.configurado === "true") {
            return;
        }

        tablaIntegrantes.dataset.configurado = "true";

        function filtrarIntegrantes() {

            const texto = buscarIntegrante?.value.toLowerCase().trim() || "";
            const rolSeleccionado = filtroRol?.value.toLowerCase() || "";

            const filas = tablaIntegrantes.querySelectorAll("tr[data-integrante]");

            let visibles = 0;

             filas.forEach(fila => {

                const nombre = fila.dataset.nombre?.toLowerCase() || "";
                const programa = fila.dataset.programa?.toLowerCase() || "";
                const rol = fila.dataset.rol?.toLowerCase() || "";

                const coincideTexto =
                    nombre.includes(texto) || programa.includes(texto);

                const coincideRol =
                    !rolSeleccionado || rol === rolSeleccionado;

                const mostrar = coincideTexto && coincideRol;

                fila.style.display = mostrar ? "" : "none";

                if (mostrar) {
                    visibles++;
                }
            });

            if (totalIntegrantes) {
                totalIntegrantes.textContent = visibles;
            }
        }

        buscarIntegrante?.addEventListener("input", filtrarIntegrantes);
        filtroRol?.addEventListener("change", filtrarIntegrantes);

        filtrarIntegrantes();
    }

    // ========================================
    // MODULO SOLICITUDES
    // ========================================

        async function configurarModuloSolicitudes() {

        const tablaSolicitudes = document.getElementById("tablaSolicitudes");
        const totalSolicitudes = document.getElementById("totalSolicitudesPendientes");

        if (!tablaSolicitudes) {
            return;
        }

        const escaparHTML = texto => String(texto ?? "").replace(
            /[&<>"']/g,
            c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
        );

                async function dibujarRegistros() {

            const tablaRegistros = document.getElementById("tablaRegistros");

            if (!tablaRegistros) {
                return;
            }

            try {
                const respuesta = await fetch("/docentelider/api/registros");

                if (!respuesta.ok) {
                    throw new Error("Error " + respuesta.status);
                }

                const registros = await respuesta.json();

                if (registros.length === 0) {
                    tablaRegistros.innerHTML = `
                        <tr>
                            <td colspan="4" class="solicitudes-vacio">
                                No hay cuentas pendientes.
                            </td>
                        </tr>`;
                    return;
                }

                tablaRegistros.innerHTML = registros.map(r => `
                    <tr>
                        <td>${escaparHTML(r.nombre)}</td>
                        <td>${escaparHTML(r.programa)}</td>
                        <td>${escaparHTML(r.correo)}</td>
                        <td>${escaparHTML(r.fecha)}</td>
                    </tr>
                `).join("");

            } catch (error) {
                console.error("No se pudieron cargar los registros:", error);
                tablaRegistros.innerHTML = `
                    <tr>
                        <td colspan="4" class="solicitudes-vacio">
                            No fue posible cargar las cuentas pendientes.
                        </td>
                    </tr>`;
            }
        }

        async function dibujarSolicitudes() {

            tablaSolicitudes.innerHTML = `
                <tr>
                    <td colspan="5" class="solicitudes-vacio">Cargando solicitudes...</td>
                </tr>`;

            try {
                const respuesta = await fetch("/docentelider/api/vinculaciones");

                if (!respuesta.ok) {
                    throw new Error("Error " + respuesta.status);
                }

                const solicitudes = await respuesta.json();

                if (totalSolicitudes) {
                    totalSolicitudes.textContent = solicitudes.length;
                }

                if (solicitudes.length === 0) {
                    tablaSolicitudes.innerHTML = `
                        <tr>
                            <td colspan="5" class="solicitudes-vacio">
                                No hay solicitudes pendientes.
                            </td>
                        </tr>`;
                    return;
                }

                tablaSolicitudes.innerHTML = solicitudes.map(s => `
                    <tr data-solicitud="${s.id}">
                        <td>${escaparHTML(s.nombre)}</td>
                        <td>${escaparHTML(s.programa)} · Semestre ${escaparHTML(s.semestre)}</td>
                        <td>Ingreso al semillero · ${escaparHTML(s.fecha)}</td>
                        <td><span class="solicitudes-estado">Pendiente</span></td>
                        <td>
                            <div class="solicitudes-acciones">
                                <button type="button" class="btn-aprobar"
                                        data-accion="aceptar" data-id="${s.id}">Aceptar</button>
                                <button type="button" class="btn-rechazar"
                                        data-accion="rechazar" data-id="${s.id}">Rechazar</button>
                            </div>
                        </td>
                    </tr>
                `).join("");

            } catch (error) {
                console.error("No se pudieron cargar las solicitudes:", error);
                tablaSolicitudes.innerHTML = `
                    <tr>
                        <td colspan="5" class="solicitudes-vacio">
                            No fue posible cargar las solicitudes.
                        </td>
                    </tr>`;
            }
        }

        tablaSolicitudes.onclick = async function (evento) {

            const boton = evento.target.closest("button[data-accion]");

            if (!boton) {
                return;
            }

            if (boton.dataset.accion === "rechazar" &&
                !confirm("¿Deseas rechazar esta solicitud?")) {
                return;
            }

            boton.disabled = true;

            try {
                const respuesta = await fetch(
                    "/docentelider/api/vinculaciones/" +
                    boton.dataset.id + "/" + boton.dataset.accion,
                    { method: "POST" }
                );
                const resultado = await respuesta.json();

                if (!respuesta.ok) {
                    alert(resultado.mensaje || "No fue posible procesar la solicitud.");
                }
            } catch (error) {
                alert("No fue posible procesar la solicitud.");
            }

            dibujarSolicitudes();
        };

        dibujarSolicitudes();
        dibujarRegistros();
    }
    // ========================================
    // MODULO CONVOCATORIAS
    // ========================================

    function configurarModuloConvocatorias() {

        const tablaConvocatorias = document.getElementById("tablaConvocatorias");

        if (!tablaConvocatorias) {
            return;
        }

        const filas = tablaConvocatorias.querySelectorAll(
            "tr[data-convocatoria]"
        );

        const totalConvocatorias = document.getElementById("totalConvocatorias");
        const totalInscripciones = document.getElementById("totalInscripciones");

        if (totalConvocatorias) {
            totalConvocatorias.textContent = filas.length;
        }

        if (totalInscripciones) {
            totalInscripciones.textContent = tablaConvocatorias.querySelectorAll(
                '[data-inscripcion="realizada"]'
            ).length;
        }
    }

    // ========================================
    // MODULO EVENTOS
    // ========================================

    function configurarModuloEventos() {

        const tablaEventos = document.getElementById("tablaEventos");

        if (!tablaEventos) {
            return;
        }

        const filas = tablaEventos.querySelectorAll("tr[data-evento]");

        const totalEventos = document.getElementById("totalEventos");
        const totalParticipaciones = document.getElementById("totalParticipaciones");

        if (totalEventos) {
            totalEventos.textContent = filas.length;
        }

        if (totalParticipaciones) {
            totalParticipaciones.textContent = tablaEventos.querySelectorAll(
                '[data-participacion="registrada"]'
            ).length;
        }
    }

    // ========================================
    // MODULO LOGROS
    // ========================================

    function configurarModuloLogros() {

        const tablaLogros = document.getElementById("tablaLogros");

        if (!tablaLogros || tablaLogros.dataset.configurado === "true") {
            return;
        }

        tablaLogros.dataset.configurado = "true";

        const buscarLogro = document.getElementById("buscarLogro");
        const filtroEstado = document.getElementById("filtroEstadoLogro");

        const totalPendientes = document.getElementById("totalLogrosPendientes");
        const totalRevision = document.getElementById("totalLogrosRevision");
        const totalAprobados = document.getElementById("totalLogrosAprobados");
        const totalRechazados = document.getElementById("totalLogrosRechazados");

        function actualizarLogros() {

            const filas = tablaLogros.querySelectorAll("tr[data-logro]");

            let pendientes = 0;
            let revision = 0;
            let aprobados = 0;
            let rechazados = 0;

            const texto = buscarLogro?.value.toLowerCase().trim() || "";
            const estadoSeleccionado = filtroEstado?.value.toLowerCase() || "";

            filas.forEach(fila => {

                const estudiante = fila.dataset.estudiante?.toLowerCase() || "";
                const titulo = fila.dataset.titulo?.toLowerCase() || "";
                const estado = fila.dataset.estado?.toLowerCase() || "";

                if (estado === "pendiente") pendientes++;
                if (estado === "en validación") revision++;
                if (estado === "aprobado") aprobados++;
                if (estado === "rechazado") rechazados++;

                const coincideTexto =
                    estudiante.includes(texto) || titulo.includes(texto);

                const coincideEstado =
                    !estadoSeleccionado || estado === estadoSeleccionado;

                fila.style.display =
                    coincideTexto && coincideEstado ? "" : "none";
            });

            if (totalPendientes) totalPendientes.textContent = pendientes;
            if (totalRevision) totalRevision.textContent = revision;
            if (totalAprobados) totalAprobados.textContent = aprobados;
            if (totalRechazados) totalRechazados.textContent = rechazados;
        }

        buscarLogro?.addEventListener("input", actualizarLogros);
        filtroEstado?.addEventListener("change", actualizarLogros);

        actualizarLogros();
    }

    // ========================================
    // MODULO PUBLICACIONES
    // ========================================

    function configurarModuloPublicaciones() {

        const formulario = document.getElementById("formPublicacion");
        const archivo = document.getElementById("archivoPublicacion");
        const nombreArchivo = document.getElementById("nombreArchivoPublicacion");
        const listaPublicaciones = document.getElementById("listaPublicaciones");

        if (!listaPublicaciones || listaPublicaciones.dataset.configurado === "true") {
            return;
        }

        listaPublicaciones.dataset.configurado = "true";

        archivo?.addEventListener("change", () => {

            if (nombreArchivo) {
                nombreArchivo.textContent = archivo.files.length
                    ? archivo.files[0].name
                    : "";
            }
        });

        function actualizarContadores() {

            const publicaciones = listaPublicaciones.querySelectorAll(
                "[data-publicacion]"
            );

            const academicas = listaPublicaciones.querySelectorAll(
                '[data-tipo="academica"]'
            );

            const totalPublicaciones = document.getElementById("totalPublicaciones");
            const totalAcademicas = document.getElementById("totalAcademicas");

            if (totalPublicaciones) {
                totalPublicaciones.textContent = publicaciones.length;
            }

            if (totalAcademicas) {
                totalAcademicas.textContent = academicas.length;
            }
        }

        formulario?.addEventListener("submit", event => {

            event.preventDefault();

            alert(
                "El formulario quedará conectado cuando implementemos el registro de publicaciones."
            );
        });

        actualizarContadores();
    }

    // ========================================
    // MODULO RANKING
    // ========================================

    function configurarModuloRanking() {

        const pestanas = document.querySelectorAll(".ranking-pestana");
        const listas = document.querySelectorAll(".ranking-lista");

        if (!pestanas.length || pestanas[0].dataset.configurado === "true") {
            return;
        }

        pestanas.forEach(pestana => {

            pestana.dataset.configurado = "true";

            pestana.addEventListener("click", () => {

                const rankingSeleccionado = pestana.dataset.ranking;

                pestanas.forEach(item => {
                    item.classList.remove("activa");
                });

                pestana.classList.add("activa");

                listas.forEach(lista => {
                    lista.classList.remove("activa");
                });

                if (rankingSeleccionado === "estudiantes") {
                    document.getElementById("rankingEstudiantes")?.classList.add("activa");
                }

                if (rankingSeleccionado === "semilleros") {
                    document.getElementById("rankingSemilleros")?.classList.add("activa");
                }
            });
        });
    }

    // ========================================
    // CAMBIAR DE MODULO
    // ========================================

    async function mostrarModulo(id) {

        const moduloExiste = document.getElementById(id);

        if (!moduloExiste || !titulos[id]) {
            return;
        }

        // CARGAR PERFIL

        if (id === "perfil") {
            await cargarHTMLPerfil();
        }

        // CARGAR SEMILLEROS

        if (id === "semilleros") {
            await cargarHTMLSemilleros();
        }

        // CARGAR HTML DE LOS DEMAS MODULOS

        if (RUTAS_MODULOS[id]) {
            await cargarHTMLModulo(id);
        }
        // CONFIGURAR USUARIO

        if (id === "usuario") {
            configurarModuloUsuario();
        }

        // CONFIGURAR SOLICITUDES

        if (id === "solicitudes") {
            configurarModuloSolicitudes();
        }

        // CONFIGURAR PROYECTOS

        if (id === "proyectos") {
            configurarModuloProyectos();
        }

        // CONFIGURAR CONVOCATORIAS

        if (id === "convocatorias") {
            configurarModuloConvocatorias();
        }

        // CONFIGURAR EVENTOS

        if (id === "eventos") {
            configurarModuloEventos();
        }

        // CONFIGURAR LOGROS

        if (id === "logros") {
            configurarModuloLogros();
        }

        // CONFIGURAR PUBLICACIONES

        if (id === "publicaciones") {
            configurarModuloPublicaciones();
        }

        // CONFIGURAR RANKING

        if (id === "ranking") {
            configurarModuloRanking();
        }

        // OCULTAR LOS MODULOS

        modulos.forEach(modulo => {
            modulo.hidden = true;
        });

        // MOSTRAR MODULO SELECCIONADO

        moduloExiste.hidden = false;

        // ACTUALIZAR TITULO

        if (tituloModulo) {
            tituloModulo.textContent = titulos[id];
        }

        // ACTUALIZAR MENU ACTIVO

        enlacesMenu.forEach(enlace => {

            enlace.classList.toggle(
                "activo",
                enlace.dataset.modulo === id
            );
        });

        // CERRAR MENU MOVIL

        sidebar?.classList.remove("abierto");
    }

    window.mostrarModulo = mostrarModulo;

    // ========================================
    // EVENTOS DEL MENU
    // ========================================

    enlacesMenu.forEach(enlace => {

        enlace.addEventListener("click", event => {

            event.preventDefault();

            mostrarModulo(enlace.dataset.modulo);
        });
    });

    // ========================================
    // NOTIFICACIONES
    // ========================================

    const btnNotificaciones = document.getElementById("btnNotificaciones");
    const panelNotificaciones = document.getElementById("panelNotificaciones");

    btnNotificaciones?.addEventListener("click", () => {

        if (!panelNotificaciones) {
            return;
        }

        const abierto = !panelNotificaciones.hidden;

        panelNotificaciones.hidden = abierto;

        btnNotificaciones.setAttribute(
            "aria-expanded",
            String(!abierto)
        );
    });

    document.addEventListener("click", event => {

        if (
            panelNotificaciones &&
            btnNotificaciones &&
            !panelNotificaciones.hidden &&
            !panelNotificaciones.contains(event.target) &&
            !btnNotificaciones.contains(event.target)
        ) {

            panelNotificaciones.hidden = true;

            btnNotificaciones.setAttribute("aria-expanded", "false");
        }
    });

    // ========================================
    // CERRAR SESION
    // ========================================

    const modalCerrarSesion = document.getElementById("modalCerrarSesion");
    const enlaceCerrarSesion = document.querySelector(".cerrar-sesion");
    const cancelarCerrarSesion = document.getElementById("cancelarCerrarSesion");
    const confirmarCerrarSesion = document.getElementById("confirmarCerrarSesion");

    enlaceCerrarSesion?.addEventListener("click", event => {

        event.preventDefault();

        if (modalCerrarSesion) {
            modalCerrarSesion.hidden = false;
        }
    });

    cancelarCerrarSesion?.addEventListener("click", () => {

        if (modalCerrarSesion) {
            modalCerrarSesion.hidden = true;
        }
    });

    confirmarCerrarSesion?.addEventListener("click", () => {

        window.location.href = "/cerrar-sesion";
    });

    consultarPerfil().catch(error => {
        console.error("No se pudo cargar la identidad:", error);
    });

    // ========================================
    // MOSTRAR INICIO AL ENTRAR
    // ========================================

    mostrarModulo("inicio");

});

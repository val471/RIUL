
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

        async function configurarModuloProyectos() {

        const tablaProyectos = document.getElementById("tablaProyectos");

        if (!tablaProyectos) {
            return;
        } 

        const total = document.getElementById("totalProyectos");
        const activos = document.getElementById("proyectosActivos");
        const revision = document.getElementById("proyectosRevision");

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        function mensajeVacio(texto) {
            tablaProyectos.innerHTML =
                '<tr><td colspan="4" class="proyectos-vacio">' + texto + "</td></tr>";
            if (total) total.textContent = 0;
            if (activos) activos.textContent = 0;
            if (revision) revision.textContent = 0;
        }

        // ----- Formulario "Cargar proyecto" -----
        const btnCargar = document.getElementById("btnCargarProyecto");
        const form = document.getElementById("formProyecto");
        const msgProyecto = document.getElementById("mensajeProyecto");

        if (btnCargar && form && form.dataset.configurado !== "true") {

            form.dataset.configurado = "true";

            const mostrarMsg = (texto) => {
                msgProyecto.textContent = texto;
                msgProyecto.hidden = false;
            };

            btnCargar.addEventListener("click", () => {
                form.reset();
                msgProyecto.hidden = true;
                document.getElementById("inicioProyecto").value =
                    new Date().toLocaleDateString("en-CA");
                form.style.display = "grid";
            });

            document.getElementById("cancelarProyecto")
                .addEventListener("click", () => {
                    form.style.display = "none";
                });

            form.addEventListener("submit", async (e) => {
                e.preventDefault();
                mostrarMsg("Guardando...");

                try {
                    const r = await fetch("/docentelider/api/proyectos", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            titulo: document.getElementById("tituloProyecto").value,
                            descripcion: document.getElementById("descripcionProyecto").value,
                            inicio: document.getElementById("inicioProyecto").value
                        })
                    });

                    if (sesionVencida(r)) {
                        return;
                    }

                    const datos = await r.json();
                    mostrarMsg(datos.mensaje);

                    if (r.ok) {
                        form.style.display = "none";
                        configurarModuloProyectos();
                    }
                } catch (error) {
                    mostrarMsg("No fue posible conectar con el servidor.");
                }
            });
        }

        // ----- Listar proyectos desde MySQL -----
        try {

            const respuesta = await fetch("/docentelider/api/proyectos");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const proyectos = await respuesta.json();

            if (proyectos.length === 0) {
                mensajeVacio("Todavía no has cargado proyectos.");
                return;
            }

            tablaProyectos.innerHTML = proyectos.map(p => `
                <tr data-proyecto data-estado="${esc(p.estado)}">
                    <td>${esc(p.titulo)}<br><small>${esc(p.descripcion)}</small></td>
                    <td>${esc(p.inicio)}</td>
                    <td>${esc(p.avances)}</td>
                    <td>${esc(p.estado)}</td>
                </tr>
            `).join("");

            if (total) {
                total.textContent = proyectos.length;
            }

            if (activos) {
                activos.textContent = proyectos.filter(
                    p => p.estado === "Activo"
                ).length;
            }

            if (revision) {
                revision.textContent = proyectos.filter(
                    p => p.estado === "En revisión"
                ).length;
            }

        } catch (error) {
            console.error("Error al cargar proyectos:", error);
            mensajeVacio("No se pudieron cargar los proyectos.");
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


    async function configurarModuloUsuario() {

        const buscarIntegrante = document.getElementById("buscarIntegrante");
        const filtroSemestre = document.getElementById("filtroSemestre");
        const tablaIntegrantes = document.getElementById("tablaIntegrantes");
        const totalIntegrantes = document.getElementById("totalIntegrantes");

        if (!tablaIntegrantes) {
            return;
        }

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        function mensajeVacio(texto) {
            tablaIntegrantes.innerHTML =
                '<tr><td colspan="5" class="usuario-vacio">' + texto + "</td></tr>";
            if (totalIntegrantes) {
                totalIntegrantes.textContent = 0;
            }
        }

        function filtrarIntegrantes() {

            const texto = buscarIntegrante?.value.toLowerCase().trim() || "";
            const semestre = filtroSemestre?.value || "";

            const filas = tablaIntegrantes.querySelectorAll("tr[data-integrante]");
            let visibles = 0; 

            filas.forEach(fila => {

                const nombre = fila.dataset.nombre.toLowerCase();
                const programa = fila.dataset.programa.toLowerCase();

                const coincideTexto =
                    nombre.includes(texto) || programa.includes(texto);
                const coincideSemestre =
                    !semestre || fila.dataset.semestre === semestre;

                const mostrar = coincideTexto && coincideSemestre;
                fila.style.display = mostrar ? "" : "none";

                if (mostrar) {
                    visibles++;
                }
            });

            if (totalIntegrantes) {
                totalIntegrantes.textContent = visibles;
            }
        }

        // Los filtros se conectan una sola vez
        if (tablaIntegrantes.dataset.configurado !== "true") {
            tablaIntegrantes.dataset.configurado = "true";
            buscarIntegrante?.addEventListener("input", filtrarIntegrantes);
            filtroSemestre?.addEventListener("change", filtrarIntegrantes);
        }

        try {

            const respuesta = await fetch("/docentelider/api/integrantes");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const integrantes = await respuesta.json();

            if (integrantes.length === 0) {
                mensajeVacio("Tu semillero todavía no tiene integrantes.");
                return;
            }

            tablaIntegrantes.innerHTML = integrantes.map(i => `
                <tr data-integrante
                    data-nombre="${esc(i.nombre)}"
                    data-programa="${esc(i.programa)}"
                    data-semestre="${esc(i.semestre)}">
                    <td>${esc(i.nombre)}<br><small>${esc(i.correo)}</small></td>
                    <td>${esc(i.programa)}</td>
                    <td>${esc(i.semestre)}</td>
                    <td>${esc(i.nivel)}</td>
                    <td>${esc(i.ingreso)}</td>
                </tr>
            `).join("");

            const semestres = [...new Set(integrantes.map(i => i.semestre))]
                .sort((a, b) => a - b);

            filtroSemestre.innerHTML =
                '<option value="">Todos los semestres</option>' +
                semestres.map(s =>
                    `<option value="${s}">Semestre ${s}</option>`
                ).join("");

            filtrarIntegrantes();

        } catch (error) {
            console.error("Error al cargar integrantes:", error);
            mensajeVacio("No se pudieron cargar los integrantes.");
        }
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

        async function configurarModuloConvocatorias() {

        const tablaConvocatorias = document.getElementById("tablaConvocatorias");

        if (!tablaConvocatorias) {
            return;
        } 

        const totalConvocatorias = document.getElementById("totalConvocatorias");
        const totalInscripciones = document.getElementById("totalInscripciones");

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        const MODALIDADES = {
            semillero: "Semillero",
            ambas: "Semillero o individual"
        };

        function mensajeVacio(texto) {
            tablaConvocatorias.innerHTML =
                '<tr><td colspan="6" class="convocatorias-vacio">' + texto + "</td></tr>";
            if (totalConvocatorias) totalConvocatorias.textContent = 0;
        }

        try {

            const respuesta = await fetch("/docentelider/api/convocatorias");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const datos = await respuesta.json();
            const convocatorias = datos.convocatorias;

            if (totalInscripciones) {
                totalInscripciones.textContent = datos.inscripciones;
            }

            if (convocatorias.length === 0) {
                mensajeVacio("Todavía no hay convocatorias disponibles.");
                return;
            }

            tablaConvocatorias.innerHTML = convocatorias.map(c => `
                <tr data-convocatoria="${c.id}">
                    <td>${esc(c.titulo)}<br><small>${esc(c.descripcion)}</small></td>
                    <td>${esc(c.inicio)}</td>
                    <td>${esc(c.cierre)}</td>
                    <td>${esc(MODALIDADES[c.modalidad] || c.modalidad)}</td>
                    <td>${c.inscrito ? "Inscrito" : "Disponible"}</td>
                    <td>—</td>
                </tr>
            `).join("");

            if (totalConvocatorias) {
                totalConvocatorias.textContent = convocatorias.length;
            }

        } catch (error) {
            console.error("Error al cargar convocatorias:", error);
            mensajeVacio("No se pudieron cargar las convocatorias.");
        }
    }

    // ========================================
    // MODULO EVENTOS
    // ========================================

        async function configurarModuloEventos() {

        const tablaEventos = document.getElementById("tablaEventos");

        if (!tablaEventos) {
            return;
        }

        const totalEventos = document.getElementById("totalEventos");
        const totalParticipaciones = document.getElementById("totalParticipaciones");

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        const MODALIDADES = {
            semillero: "Semillero",
            ambas: "Semillero o individual"
        };

        function mensajeVacio(texto) {
            tablaEventos.innerHTML =
                '<tr><td colspan="7" class="eventos-vacio">' + texto + "</td></tr>";
            if (totalEventos) totalEventos.textContent = 0;
        }

        try {

            const respuesta = await fetch("/docentelider/api/eventos");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const datos = await respuesta.json();
            const eventos = datos.eventos;

            if (totalParticipaciones) {
                totalParticipaciones.textContent = datos.participaciones;
            }

            if (eventos.length === 0) {
                mensajeVacio("Todavía no hay eventos disponibles.");
                return;
            }

            tablaEventos.innerHTML = eventos.map(e => `
                <tr data-evento="${e.id}">
                    <td>${esc(e.nombre)}<br><small>${esc(e.descripcion)}</small></td>
                    <td>${esc(e.fecha)}</td>
                    <td>${esc(e.lugar)}</td>
                    <td>${esc(MODALIDADES[e.modalidad] || e.modalidad)}</td>
                    <td>${esc(e.participantes)}</td>
                    <td>${e.finalizado ? "Finalizado" : "Próximo"}</td>
                    <td>—</td>
                </tr>
            `).join("");

            if (totalEventos) {
                totalEventos.textContent =
                    eventos.filter(e => !e.finalizado).length;
            }

        } catch (error) {
            console.error("Error al cargar eventos:", error);
            mensajeVacio("No se pudieron cargar los eventos.");
        }
    }

    // ========================================
    // MODULO LOGROS
    // ========================================

        async function configurarModuloLogros() {

        const tablaLogros = document.getElementById("tablaLogros");

        if (!tablaLogros) {
            return;
        }

        const buscarLogro = document.getElementById("buscarLogro");
        const filtroEstado = document.getElementById("filtroEstadoLogro");

        const totalPendientes = document.getElementById("totalLogrosPendientes");
        const totalRevision = document.getElementById("totalLogrosRevision");
        const totalAprobados = document.getElementById("totalLogrosAprobados");
        const totalRechazados = document.getElementById("totalLogrosRechazados");

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        const ESTADOS = {
            PENDIENTE: "Pendiente",
            EN_VALIDACION: "En validación",
            APROBADO: "Aprobado",
            RECHAZADO: "Rechazado"
        };

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

        // Los filtros se conectan una sola vez
        if (tablaLogros.dataset.configurado !== "true") {
            tablaLogros.dataset.configurado = "true";
            buscarLogro?.addEventListener("input", actualizarLogros);
            filtroEstado?.addEventListener("change", actualizarLogros);
        }

        function mensajeVacio(texto) {
            tablaLogros.innerHTML =
                '<tr><td colspan="7" class="logros-vacio">' + texto + "</td></tr>";
            actualizarLogros();
        }

        try {

            const respuesta = await fetch("/docentelider/api/logros");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const logros = await respuesta.json();

            if (logros.length === 0) {
                mensajeVacio("Todavía no hay logros registrados.");
                return;
            }

            tablaLogros.innerHTML = logros.map(l => {

                const estado = ESTADOS[l.estado] || l.estado;

                return `
                <tr data-logro="${l.id}"
                    data-estudiante="${esc(l.estudiante)}"
                    data-titulo="${esc(l.titulo)}"
                    data-estado="${esc(estado)}">
                    <td>${esc(l.estudiante)}</td>
                    <td>${esc(l.titulo)}<br><small>${esc(l.descripcion)}</small></td>
                    <td>${esc(l.tipo)}</td>
                    <td>${esc(l.fecha)}</td>
                    <td>${esc(estado)}</td>
                    <td>${l.calidad === null ? "—" : esc(l.calidad) + "%"}</td>
                    <td>—</td>
                </tr>`;
            }).join("");

            actualizarLogros();

        } catch (error) {
            console.error("Error al cargar logros:", error);
            mensajeVacio("No se pudieron cargar los logros.");
        }
    }

   // ========================================
    // MODULO PUBLICACIONES
    // ========================================
          async function configurarModuloPublicaciones() {

        const formulario = document.getElementById("formPublicacion");
        const contenido = document.getElementById("contenidoPublicacion");
        const academica = document.getElementById("publicacionAcademica");
        const archivo = document.getElementById("archivoPublicacion");
        const nombreArchivo = document.getElementById("nombreArchivoPublicacion");
        const btnPublicar = document.getElementById("btnPublicar");
        const listaPublicaciones = document.getElementById("listaPublicaciones");

        if (!listaPublicaciones) {
            return;
        }

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        // ----- COMENTARIOS -----
        async function cargarComentarios(id) {

            const caja = document.getElementById("comentarios-" + id);

            if (!caja) {
                return;
            }

            try {

                const r = await fetch(
                    "/docentelider/api/publicaciones/" + id + "/comentarios"
                );

                if (sesionVencida(r)) {
                    return;
                }

                if (!r.ok) {
                    throw new Error("Error " + r.status);
                }

                const comentarios = await r.json();

                caja.innerHTML = comentarios.map(c => `
                    <div style="padding:8px 0;">
                        <strong>${esc(c.autor)}</strong>
                        <small>${esc(c.fecha)}</small>
                        <p style="margin:4px 0 0; white-space:pre-wrap;">${esc(c.contenido)}</p>
                    </div>
                `).join("") + `
                    <div style="display:flex; gap:8px; margin-top:10px;">
                        <input type="text" class="campo-comentario" maxlength="1000"
                               placeholder="Escribe un comentario..."
                               style="flex:1; padding:8px;">
                        <button type="button" class="btn-enviar-comentario"
                                data-id="${id}">Comentar</button>
                    </div>
                `;

                const boton = listaPublicaciones.querySelector(
                    '.btn-comentarios[data-id="' + id + '"]'
                );

                if (boton) {
                    boton.textContent = "💬 Comentarios (" + comentarios.length + ")";
                }

            } catch (error) {
                console.error("Error al cargar comentarios:", error);
                caja.innerHTML = "<small>No se pudieron cargar los comentarios.</small>";
            }
        }

        // ----- PUBLICACIONES -----
        async function cargarPublicaciones() {

            try {

                const respuesta = await fetch("/docentelider/api/publicaciones");

                if (sesionVencida(respuesta)) {
                    return;
                }

                if (!respuesta.ok) {
                    throw new Error("Error " + respuesta.status);
                }

                const datos = await respuesta.json();

                const totalPublicaciones = document.getElementById("totalPublicaciones");
                const totalAcademicas = document.getElementById("totalAcademicas");

                if (totalPublicaciones) totalPublicaciones.textContent = datos.total;
                if (totalAcademicas) totalAcademicas.textContent = datos.academicas;

                if (datos.publicaciones.length === 0) {
                    listaPublicaciones.innerHTML =
                        '<div class="publicaciones-vacio">Todavía no hay publicaciones disponibles.</div>';
                    return;
                }

                listaPublicaciones.innerHTML = datos.publicaciones.map(p => `
                   <article class="publicacion-card" data-publicacion="${p.id}"
                            data-tipo="${p.academica ? "academica" : "general"}">
                        </div>class="publicacion-cabecera">
                            <div class="publicacion-autor">
                                <div class="publicacion-avatar">
                                    ${esc(p.autor).charAt(0).toUpperCase()}
                        </div>
                    
                        <div>
                           <strong>
                               ${esc(p.autor)}${p.propia ? " (tú)" : ""}
                           </strong>

                        
                    <span>
                        ${esc(p.fecha)}
                        · ${p.academica ? "Publicación académica" : "Publicación general"}
                    </span>

                     ${p.semillero ? `
                        <small>${esc(p.semillero)}</small>
                    ` : ""}
                </div>
             </div>
            </div>


                        <footer style="margin-top:14px; border-top:1px solid #eee; padding-top:10px;">
                            <div style="display:flex; gap:12px;">
                                <button type="button" class="btn-reaccion" data-id="${p.id}">
                                    ${p.yo_reaccione ? "❤️" : "🤍"} Me gusta (${p.reacciones})
                                </button>
                                <button type="button" class="btn-comentarios" data-id="${p.id}">
                                    💬 Comentarios (${p.comentarios})
                                </button>
                            </div>
                            <div class="caja-comentarios" id="comentarios-${p.id}" hidden></div>
                        </footer>
                    </article>
                `).join("");

            } catch (error) {
                console.error("Error al cargar publicaciones:", error);
                listaPublicaciones.innerHTML =
                    '<div class="publicaciones-vacio">No se pudieron cargar las publicaciones.</div>';
            }
        }

        // Los eventos se conectan una sola vez
        if (listaPublicaciones.dataset.configurado !== "true") {

            listaPublicaciones.dataset.configurado = "true";

            archivo?.addEventListener("change", () => {
                if (nombreArchivo) {
                    nombreArchivo.textContent = archivo.files.length
                        ? archivo.files[0].name
                        : "";
                }
            });

            formulario?.addEventListener("submit", async event => {

                event.preventDefault();

                btnPublicar.disabled = true;

                try {

                    const respuesta = await fetch("/docentelider/api/publicaciones", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            contenido: contenido.value,
                            academica: academica.checked
                        })
                    });

                    if (sesionVencida(respuesta)) {
                        return;
                    }

                    const datos = await respuesta.json();

                    if (!respuesta.ok) {
                        alert(datos.mensaje);
                        return;
                    }

                    formulario.reset();
                    if (nombreArchivo) nombreArchivo.textContent = "";
                    await cargarPublicaciones();

                } catch (error) {
                    alert("No fue posible conectar con el servidor.");
                } finally {
                    btnPublicar.disabled = false;
                }
            });

            // Abrir comentarios y enviar un comentario
            listaPublicaciones.addEventListener("click", async e => {

                const reaccion = e.target.closest(".btn-reaccion");

                if (reaccion) {

                    reaccion.disabled = true;

                    try {

                        const r = await fetch(
                            "/docentelider/api/publicaciones/" +
                            reaccion.dataset.id + "/reaccion",
                            { method: "POST" }
                        );

                        if (sesionVencida(r)) {
                            return;
                        }

                        const datos = await r.json();

                        if (!r.ok) {
                            alert(datos.mensaje);
                            return;
                        }

                        reaccion.textContent =
                            (datos.reaccionado ? "❤️" : "🤍") +
                            " Me gusta (" + datos.total + ")";

                    } catch (error) {
                        alert("No fue posible conectar con el servidor.");
                    } finally {
                        reaccion.disabled = false;
                    }

                    return;
                }

                const boton = e.target.closest(".btn-comentarios");

                if (boton) {
                    const caja = document.getElementById("comentarios-" + boton.dataset.id);

                    if (!caja.hidden) {
                        caja.hidden = true;
                        return;
                    }

                    caja.hidden = false;
                    await cargarComentarios(boton.dataset.id);
                    return;
                }

                const enviar = e.target.closest(".btn-enviar-comentario");

                if (enviar) {
                    const id = enviar.dataset.id;
                    const campo = enviar.parentElement.querySelector(".campo-comentario");
                    const texto = campo.value.trim();

                    if (!texto) {
                        return;
                    }

                    enviar.disabled = true;

                    try {

                        const r = await fetch(
                            "/docentelider/api/publicaciones/" + id + "/comentarios",
                            {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ contenido: texto })
                            }
                        );

                        if (sesionVencida(r)) {
                            return;
                        }

                        const datos = await r.json();

                        if (!r.ok) {
                            alert(datos.mensaje);
                            return;
                        }

                        await cargarComentarios(id);

                    } catch (error) {
                        alert("No fue posible conectar con el servidor.");
                    } finally {
                        enviar.disabled = false;
                    }
                }
            });

            // Enviar el comentario con la tecla Enter
            listaPublicaciones.addEventListener("keydown", e => {

                if (e.key === "Enter" &&
                    e.target.classList.contains("campo-comentario")) {

                    e.preventDefault();
                    e.target.parentElement
                        .querySelector(".btn-enviar-comentario")
                        .click();
                }
            });
        }

        await cargarPublicaciones();
    } 
    // ========================================
    // MODULO RANKING
    // ========================================

        async function configurarModuloRanking() {

        const pestanas = document.querySelectorAll(".ranking-pestana");
        const listas = document.querySelectorAll(".ranking-lista");

        if (!pestanas.length) {
            return;
        }

        // Las pestañas se conectan una sola vez
        if (pestanas[0].dataset.configurado !== "true") {

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

        const esc = (t) => String(t ?? "").replace(/[&<>"']/g, (c) => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;",
            '"': "&quot;", "'": "&#39;"
        }[c]));

        const tablaEstudiantes = document.getElementById("tablaRankingEstudiantes");
        const tablaSemilleros = document.getElementById("tablaRankingSemilleros");

        function pintar(tabla, filas, textoVacio) {

            if (!tabla) {
                return;
            }

            if (filas.length === 0) {
                tabla.innerHTML =
                    '<tr><td colspan="6" class="ranking-vacio">' + textoVacio + "</td></tr>";
                return;
            }

            tabla.innerHTML = filas.map(f => `
                <tr>
                    <td>${esc(f.posicion)}</td>
                    <td>${esc(f.nombre)}</td>
                    <td>${esc(f.nivel)}</td>
                    <td>${esc(f.estrellas)}</td>
                    <td>${esc(f.xp)}</td>
                    <td>${esc(f.insignias)}</td>
                </tr>
            `).join("");
        }

        try {

            const respuesta = await fetch("/docentelider/api/ranking");

            if (sesionVencida(respuesta)) {
                return;
            }

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            const datos = await respuesta.json();

            pintar(tablaEstudiantes, datos.estudiantes,
                "No hay investigadores en el ranking.");
            pintar(tablaSemilleros, datos.semilleros,
                "No hay semilleros en el ranking.");

            const posicion = document.getElementById("posicionSemillero");
            const xp = document.getElementById("xpSemillero");

            if (posicion) {
                posicion.textContent =
                    datos.mi_posicion === null ? "--" : "#" + datos.mi_posicion;
            }

            if (xp) {
                xp.textContent = datos.mi_xp;
            }

        } catch (error) {
            console.error("Error al cargar el ranking:", error);
            pintar(tablaEstudiantes, [], "No se pudo cargar el ranking.");
            pintar(tablaSemilleros, [], "No se pudo cargar el ranking.");
        }
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

        if (id === "usuarios") {
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

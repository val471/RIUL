document.addEventListener("DOMContentLoaded", () => {
    const seleccionar = (selector, contexto = document) =>
        contexto.querySelector(selector);

    const seleccionarTodos = (selector, contexto = document) =>
        [...contexto.querySelectorAll(selector)];

    // BUSCADOR DE PUBLICACIONES
    const buscadorPublicaciones = seleccionar("#buscar-publicaciones");

    buscadorPublicaciones?.addEventListener("input", () => {
        const texto = buscadorPublicaciones.value.trim().toLowerCase();

        seleccionarTodos("[data-publicacion]").forEach(publicacion => {
            const contenido = (
                publicacion.dataset.texto ||
                publicacion.textContent
            ).toLowerCase();

            publicacion.hidden = !contenido.includes(texto);
        });
    });

    // BUSCADOR DE RANKING
    const buscadorRanking = seleccionar("#buscar-ranking");

    buscadorRanking?.addEventListener("input", () => {
        const texto = buscadorRanking.value.trim().toLowerCase();
        let encontrados = 0;

        seleccionarTodos("[data-ranking]").forEach(fila => {
            const coincide = fila.textContent.toLowerCase().includes(texto);
            fila.hidden = !coincide;
            if (coincide) encontrados++;
        });

        const aviso = seleccionar("#ranking-sin-resultados");
        if (aviso) aviso.hidden = encontrados !== 0;
    });

    // FUNCIONES PARA MODALES
    function configurarModal(id, selectorAbrir, selectorCerrar, selectorFoco) {
        const modal = seleccionar(id);
        if (!modal) return;

        const abrir = () => {
            modal.hidden = false;
            document.body.style.overflow = "hidden";
            seleccionar(selectorFoco, modal)?.focus();
        };

        const cerrar = () => {
            modal.hidden = true;

            if (!seleccionar(
                ".modal-publicacion:not([hidden]), .modal-logro:not([hidden])"
            )) {
                document.body.style.overflow = "";
            }
        };

        seleccionarTodos(selectorAbrir).forEach(boton => {
            boton.addEventListener("click", abrir);
        });

        seleccionarTodos(selectorCerrar, modal).forEach(boton => {
            boton.addEventListener("click", cerrar);
        });

        modal.addEventListener("click", evento => {
            if (evento.target === modal) cerrar();
        });

        document.addEventListener("keydown", evento => {
            if (evento.key === "Escape" && !modal.hidden) cerrar();
        });

        return { abrir, cerrar };
    }

    const modalPublicacion = configurarModal(
        "#modal-publicacion",
        "[data-abrir-publicacion]",
        "[data-cerrar-publicacion]",
        "#publicacion-contenido"
    );

    const modalLogro = configurarModal(
        "#modal-logro",
        "[data-abrir-logro]",
        "[data-cerrar-logro]",
        "#logro-titulo"
    );

    // PUBLICACIONES DE DEMOSTRACIÓN
    const formularioPublicacion = seleccionar("#form-publicacion");
    const listaPublicaciones = seleccionar("#lista-publicaciones");

    function mostrarMensajePublicacion(texto) {
        const mensaje = seleccionar("#mensaje-publicaciones");
        if (mensaje) mensaje.textContent = texto;
    }

    formularioPublicacion?.addEventListener("submit", evento => {
        evento.preventDefault();

        const contenido = seleccionar("#publicacion-contenido")
            .value.trim();

        const archivo = seleccionar("#publicacion-archivo");

        if (!contenido) return;

        const publicacion = document.createElement("article");
        publicacion.className = "publicacion-card";
        publicacion.dataset.publicacion = "";
        publicacion.dataset.texto = contenido.toLowerCase();

        const autor = document.createElement("div");
        autor.className = "publicacion-autor";

        const avatar = document.createElement("span");
        avatar.className = "publicacion-avatar";
        avatar.textContent = "DL";

        const datos = document.createElement("div");
        const nombre = document.createElement("strong");
        nombre.textContent = "Docente Líder";

        const detalle = document.createElement("small");
        detalle.textContent = "Ahora · Publicación académica";

        datos.append(nombre, detalle);
        autor.append(avatar, datos);

        const texto = document.createElement("p");
        texto.className = "publicacion-texto";
        texto.textContent = contenido;

        publicacion.append(autor, texto);

        if (archivo?.files?.length) {
            const nota = document.createElement("p");
            nota.className = "texto-ayuda";
            nota.textContent =
                "Archivo seleccionado: " + archivo.files[0].name +
                ". No se ha subido al servidor.";
            publicacion.append(nota);
        }

        const acciones = document.createElement("div");
        acciones.className = "publicacion-acciones";

        [
            ["♡ Me gusta", "data-me-gusta"],
            ["☏ Comentar", "data-comentar"],
            ["♧ Compartir", "data-compartir"]
        ].forEach(([etiqueta, atributo]) => {
            const boton = document.createElement("button");
            boton.type = "button";
            boton.textContent = etiqueta;
            boton.setAttribute(atributo, "");
            acciones.append(boton);
        });

        publicacion.append(acciones);
        listaPublicaciones.prepend(publicacion);

        formularioPublicacion.reset();
        modalPublicacion?.cerrar();
        mostrarMensajePublicacion(
            "Publicación añadida a la pantalla. No se ha guardado en la base de datos."
        );
    });

    // ACCIONES DE PUBLICACIONES
    listaPublicaciones?.addEventListener("click", async evento => {
        const boton = evento.target.closest("button");
        if (!boton) return;

        const tarjeta = boton.closest("[data-publicacion]");
        if (!tarjeta) return;

        if (boton.hasAttribute("data-me-gusta")) {
            const total = seleccionar("[data-total-reacciones]", tarjeta);
            const marcado = boton.dataset.marcado === "true";

            boton.dataset.marcado = String(!marcado);
            boton.textContent = marcado ? "♡ Me gusta" : "♥ Te gusta";

            if (total) {
                total.textContent = Math.max(
                    0,
                    Number(total.textContent) + (marcado ? -1 : 1)
                );
            }
        }

        if (boton.hasAttribute("data-comentar")) {
            const zona = seleccionar(".publicacion-comentarios", tarjeta);
            if (zona) {
                zona.hidden = !zona.hidden;
                if (!zona.hidden) {
                    seleccionar("input[name='comentario']", zona)?.focus();
                }
            }
        }

        if (boton.hasAttribute("data-compartir")) {
            const texto = tarjeta.querySelector(".publicacion-texto")?.textContent
                .trim() || "Publicación RIUL";

            try {
                if (navigator.share) {
                    await navigator.share({ title: "Publicación RIUL", text: texto });
                } else if (navigator.clipboard) {
                    await navigator.clipboard.writeText(texto);
                    mostrarMensajePublicacion("Texto copiado para compartir.");
                } else {
                    mostrarMensajePublicacion("Tu navegador no permite compartir desde esta página.");
                }
            } catch (error) {
                if (error.name !== "AbortError") {
                    mostrarMensajePublicacion("No fue posible compartir la publicación.");
                }
            }
        }

        if (boton.hasAttribute("data-eliminar-publicacion")) {
            if (confirm("¿Eliminar esta publicación de la pantalla?")) {
                tarjeta.remove();
                mostrarMensajePublicacion(
                    "Publicación eliminada de la vista de demostración."
                );
            }
        }

        if (boton.hasAttribute("data-editar-publicacion")) {
            const texto = seleccionar(".publicacion-texto", tarjeta);
            if (!texto) return;

            const nuevo = prompt("Edita el contenido:", texto.textContent);
            if (nuevo === null || !nuevo.trim()) return;

            texto.textContent = nuevo.trim();
            tarjeta.dataset.texto = tarjeta.textContent.toLowerCase();
            mostrarMensajePublicacion("Publicación editada en pantalla.");
        }
    });

    listaPublicaciones?.addEventListener("submit", evento => {
        const formulario = evento.target.closest("[data-form-comentario]");
        if (!formulario) return;

        evento.preventDefault();

        const campo = seleccionar("input[name='comentario']", formulario);
        const contenido = campo?.value.trim();
        if (!contenido) return;

        const tarjeta = formulario.closest("[data-publicacion]");
        const lista = seleccionar("[data-lista-comentarios]", formulario);
        const total = seleccionar("[data-total-comentarios]", tarjeta);

        const comentario = document.createElement("p");
        comentario.className = "comentario-item";
        comentario.textContent = "Docente Líder: " + contenido;
        lista?.prepend(comentario);

        if (total) total.textContent = Number(total.textContent) + 1;
        formulario.reset();
    });

    // ARCHIVOS DE DEMOSTRACIÓN
    document.addEventListener("click", evento => {
        const enlace = evento.target.closest("[data-archivo-demo]");
        if (!enlace) return;

        evento.preventDefault();
        alert("Este archivo es ilustrativo. Para descargarlo hay que cargarlo al servidor.");
    });

    // LOGROS Y CALIFICACIÓN
    const formularioLogro = seleccionar("#form-logro");
    const listaLogros = seleccionar("#lista-logros");

    const xpBasePorTipo = {
        publicacion: 5,
        evento: 50,
        ponencia: 100,
        articulo: 150,
        proyecto: 200,
        patente: 300
    };

    function mostrarMensajeLogro(texto) {
        const mensaje = seleccionar("#mensaje-logros");
        if (mensaje) mensaje.textContent = texto;
    }

    function aplicarCalificacion(tarjeta, valor) {
        const tipo = tarjeta.dataset.tipo || "proyecto";
        const base = Number(tarjeta.dataset.xpBase) ||
            xpBasePorTipo[tipo] || 0;

        const porcentaje = Number(valor);
        if (![50, 75, 100].includes(porcentaje)) return;

        const puntos = Math.round(base * porcentaje / 100);
        const etiqueta = seleccionar("[data-logro-calificacion]", tarjeta);
        const resultado = seleccionar("[data-logro-xp]", tarjeta);
        const selector = seleccionar("[data-calificar-logro]", tarjeta);

        if (etiqueta) {
            etiqueta.textContent = porcentaje + " % · " +
                ({50: "Básico", 75: "Destacado", 100: "Excelente"}[porcentaje]);
        }

        if (resultado) {
            resultado.hidden = false;
            resultado.textContent = "XP calculado en la demostración: " + puntos;
        }

        if (selector) {
            selector.disabled = true;
            selector.setAttribute("aria-label", "Calificación aplicada");
        }

        mostrarMensajeLogro(
            "Calificación aplicada en pantalla. El XP aún no se ha guardado en el servidor."
        );
    }

    listaLogros?.addEventListener("change", evento => {
        const selector = evento.target.closest("[data-calificar-logro]");
        if (!selector || !selector.value) return;

        const tarjeta = selector.closest("[data-logro]");
        if (!tarjeta) return;

        aplicarCalificacion(tarjeta, selector.value);
    });

    formularioLogro?.addEventListener("submit", evento => {
        evento.preventDefault();

        const titulo = seleccionar("#logro-titulo").value.trim();
        const descripcion = seleccionar("#logro-descripcion").value.trim();
        const estudiante = seleccionar("#logro-estudiante").value.trim();
        const tipoSelect = seleccionar("#logro-tipo");
        const tipo = tipoSelect.value;
        const base = xpBasePorTipo[tipo];

        if (!titulo || !descripcion || !estudiante || !base) return;

        const tarjeta = document.createElement("article");
        tarjeta.className = "logro-card";
        tarjeta.dataset.logro = "";
        tarjeta.dataset.tipo = tipo;
        tarjeta.dataset.xpBase = String(base);

        const detalles = document.createElement("div");
        const nombre = document.createElement("strong");
        nombre.dataset.logroTitulo = "";
        nombre.textContent = titulo;

        const descripcionEl = document.createElement("p");
        descripcionEl.textContent = estudiante + " · " +
            tipoSelect.selectedOptions[0].textContent;

        const estado = document.createElement("small");
        estado.dataset.logroCalificacion = "";
        estado.textContent = "Sin calificar";

        detalles.append(nombre, descripcionEl, estado);

        const etiqueta = document.createElement("label");
        etiqueta.className = "logro-selector";

        const texto = document.createElement("span");
        texto.className = "solo-lectores";
        texto.textContent = "Calificar " + titulo;

        const selector = document.createElement("select");
        selector.dataset.calificarLogro = "";
        selector.setAttribute("aria-label", "Calificar " + titulo);

        [
            ["", "Calificar..."],
            ["50", "50 % · Básico"],
            ["75", "75 % · Destacado"],
            ["100", "100 % · Excelente"]
        ].forEach(([valor, textoOpcion]) => {
            const opcion = document.createElement("option");
            opcion.value = valor;
            opcion.textContent = textoOpcion;
            selector.append(opcion);
        });

        etiqueta.append(texto, selector);

        const xp = document.createElement("p");
        xp.className = "logro-xp";
        xp.dataset.logroXp = "";
        xp.hidden = true;

        tarjeta.append(detalles, etiqueta, xp);
        listaLogros.prepend(tarjeta);

        formularioLogro.reset();
        modalLogro?.cerrar();

        mostrarMensajeLogro(
            "Logro registrado en pantalla. No se ha guardado en la base de datos."
        );
    });
});

/* RIUL — PUBLICACIONES DOCENTE */
(() => {
    "use strict";

    function iniciarPublicaciones() {
        const lista = document.getElementById("pub-lista");
        if (!lista || lista.dataset.inicializada === "true") return;

        lista.dataset.inicializada = "true";

        lista.querySelectorAll(".pub-tarjeta").forEach(tarjeta => {
            tarjeta.dataset.likesBase =
                tarjeta.querySelector("[data-total-likes]")?.textContent.trim() || "0";

            tarjeta.dataset.comentariosBase =
                tarjeta.querySelector("[data-total-comentarios]")?.textContent.trim() || "0";

            tarjeta.dataset.vistasBase =
                tarjeta.querySelector("[data-total-vistas]")?.textContent.trim() || "0";
        });

        const modal = document.getElementById("pub-modal");
        const formulario = document.getElementById("pub-form-publicar");
        const descripcion = document.getElementById("pub-descripcion");
        const adjunto = document.getElementById("pub-adjunto");
        const tituloModal = document.getElementById("pub-modal-titulo");
        const buscar = document.getElementById("pub-buscar");
        const mensaje = document.getElementById("pub-mensaje");
        const sinResultados = document.getElementById("pub-sin-resultados");

        let tarjetaEditando = null;
        let urlArchivoTemporal = null;

        function avisar(texto) {
            mensaje.textContent = texto;
            mensaje.hidden = false;
        }

        function cerrarModal() {
            modal.hidden = true;
            tarjetaEditando = null;
            formulario.reset();
            tituloModal.textContent = "Crear publicación";

            if (urlArchivoTemporal) {
                URL.revokeObjectURL(urlArchivoTemporal);
                urlArchivoTemporal = null;
            }
        }

        function abrirModal(tarjeta = null) {
            tarjetaEditando = tarjeta;
            formulario.reset();

            if (urlArchivoTemporal) {
                URL.revokeObjectURL(urlArchivoTemporal);
                urlArchivoTemporal = null;
            }

            tituloModal.textContent = tarjeta
                ? "Editar publicación"
                : "Crear publicación";

            descripcion.value = tarjeta
                ? tarjeta.querySelector(".pub-texto").textContent.trim()
                : "";

            modal.hidden = false;
            descripcion.focus();
        }

        function crearElemento(etiqueta, clase, texto) {
            const elemento = document.createElement(etiqueta);
            if (clase) elemento.className = clase;
            if (texto !== undefined) elemento.textContent = texto;
            return elemento;
        }

        
        function actualizarEstadisticas(tarjeta) {
            if (!tarjeta) return;

            const contadorReacciones = tarjeta.querySelector("[data-total-likes]");
            const contadorComentarios = tarjeta.querySelector("[data-total-comentarios]");
            const contadorVistas = tarjeta.querySelector("[data-total-vistas]");

            const reacciones = Math.max(
                0,
                Number(tarjeta.dataset.likesBase) || 0
            );

            const comentariosIniciales = Math.max(
                0,
                Number(tarjeta.dataset.comentariosBase) || 0
            );

            const comentariosAgregados = tarjeta.querySelectorAll(
                ".pub-comentarios-lista .pub-comentario"
            ).length;

            if (contadorReacciones) {
                contadorReacciones.textContent = reacciones;
            }

            if (contadorComentarios) {
                contadorComentarios.textContent =
                    comentariosIniciales + comentariosAgregados;
            }

            if (contadorVistas) {
                contadorVistas.textContent =
                    tarjeta.dataset.vistasBase || "0";
            }
        }


        function crearTarjeta(texto, archivo, nombreArchivo) {
            const tarjeta = crearElemento("article", "pub-tarjeta");
            tarjeta.dataset.autor = "Docente Líder";
            tarjeta.dataset.propia = "true";
            tarjeta.dataset.comentariosBase = "0";
            tarjeta.dataset.likesBase = "0";

            const cabecera = crearElemento("div", "pub-cabecera");
            cabecera.append(
                crearElemento("div", "pub-avatar", "DL")
            );

            const autor = crearElemento("div", "pub-autor");
            autor.append(
                crearElemento("strong", "", "Docente Líder"),
                crearElemento("span", "", "Ahora · Publicación académica")
            );

            const menu = crearElemento("button", "pub-menu", "⋯");
            menu.type = "button";
            menu.dataset.accion = "menu";
            menu.setAttribute("aria-label", "Opciones");

            const opciones = crearElemento("div", "pub-opciones");
            opciones.hidden = true;

            const editar = crearElemento("button", "", "Editar");
            editar.type = "button";
            editar.dataset.accion = "editar";

            const eliminar = crearElemento("button", "", "Eliminar");
            eliminar.type = "button";
            eliminar.dataset.accion = "eliminar";

            opciones.append(editar, eliminar);
            cabecera.append(autor, menu, opciones);

            const contenido = crearElemento("div", "pub-texto", texto);

            const estadisticas = crearElemento("div", "pub-estadisticas");
            estadisticas.append(
                crearElemento("span", "", "0 reacciones"),
                crearElemento("span", "", "0 comentarios"),
                crearElemento("span", "", "0 vistas")
            );

            estadisticas.children[0].innerHTML =
                '<span data-total-likes>0</span> reacciones';
            estadisticas.children[1].innerHTML =
                '<span data-total-comentarios>0</span> comentarios';
            estadisticas.children[2].innerHTML =
                '◉ <span data-total-vistas>0</span> vistas';

            const acciones = crearElemento("div", "pub-acciones");

            [
                ["like", "♡", "Me gusta"],
                ["comentar", "▤", "Comentar"],
                ["compartir", "↗", "Compartir"]
            ].forEach(([accion, icono, etiqueta]) => {
                const boton = crearElemento(
                    "button", "", icono + " " + etiqueta
                );
                boton.type = "button";
                boton.dataset.accion = accion;

                if (accion === "like") {
                    boton.setAttribute("aria-pressed", "false");
                }

                acciones.append(boton);
            });

            const comentarios = crearElemento("div", "pub-comentarios");
            comentarios.hidden = true;

            const listaComentarios = crearElemento(
                "div", "pub-comentarios-lista"
            );

            const formularioComentario = crearElemento(
                "form", "pub-form-comentario"
            );

            const campo = crearElemento("input");
            campo.name = "comentario";
            campo.maxLength = 500;
            campo.required = true;
            campo.placeholder = "Escribe un comentario...";
            campo.setAttribute("aria-label", "Escribe un comentario");

            const enviar = crearElemento(
                "button", "pub-btn pub-btn-principal", "Enviar"
            );
            enviar.type = "submit";

            formularioComentario.append(campo, enviar);
            comentarios.append(listaComentarios, formularioComentario);

            tarjeta.append(cabecera, contenido);

            if (archivo) {
                const enlace = crearElemento("a", "pub-archivo");
                enlace.href = archivo;
                enlace.download = nombreArchivo;
                enlace.append(
                    crearElemento("span", "pub-archivo-icono", "▤")
                );

                const datosArchivo = crearElemento("span");
                datosArchivo.append(
                    crearElemento("strong", "", nombreArchivo),
                    crearElemento("small", "", "Archivo adjunto")
                );

                enlace.append(
                    datosArchivo,
                    crearElemento("span", "pub-archivo-descarga", "↗")
                );

                tarjeta.append(enlace);
            }

            tarjeta.append(estadisticas, acciones, comentarios);
            return tarjeta;
        }

        document.getElementById("pub-abrir-modal")
            .addEventListener("click", () => abrirModal());

        document.querySelectorAll('[data-accion="cerrar-modal"]')
            .forEach(boton => {
                boton.addEventListener("click", cerrarModal);
            });

        document.addEventListener("keydown", evento => {
            if (evento.key === "Escape" && !modal.hidden) {
                cerrarModal();
            }
        });

        formulario.addEventListener("submit", evento => {
            evento.preventDefault();

            const texto = descripcion.value.trim();
            if (!texto) {
                descripcion.focus();
                return;
            }

            const archivoSeleccionado = adjunto.files[0];

            if (tarjetaEditando) {
                tarjetaEditando.querySelector(".pub-texto").textContent = texto;

                if (archivoSeleccionado) {
                    const url = URL.createObjectURL(archivoSeleccionado);
                    const nuevaTarjeta = crearTarjeta(
                        texto, url, archivoSeleccionado.name
                    );

                    // Conserva las estadísticas y comentarios existentes.
                    const archivoNuevo = nuevaTarjeta.querySelector(".pub-archivo");
                    const archivoAnterior = tarjetaEditando.querySelector(".pub-archivo");

                    if (archivoAnterior) archivoAnterior.remove();
                    tarjetaEditando.querySelector(".pub-texto")
                        .after(archivoNuevo);
                }

                avisar("Publicación actualizada en esta demostración.");
            } else {
                let url = null;
                let nombre = null;

                if (archivoSeleccionado) {
                    url = URL.createObjectURL(archivoSeleccionado);
                    nombre = archivoSeleccionado.name;
                }

                const tarjeta = crearTarjeta(texto, url, nombre);
                lista.prepend(tarjeta);
                avisar("Publicación creada correctamente en esta demostración.");
            }

            cerrarModal();
            filtrarPublicaciones();
        });

        lista.addEventListener("click", async evento => {
            const boton = evento.target.closest("button[data-accion]");
            if (!boton) return;

            const tarjeta = boton.closest(".pub-tarjeta");
            if (!tarjeta) return;

            const accion = boton.dataset.accion;

            if (accion === "menu") {
                const opciones = tarjeta.querySelector(".pub-opciones");

                // Solo el autor de la publicación puede editarla o eliminarla.
                if (tarjeta.dataset.propia !== "true") {
                    avisar("Solo puedes editar o eliminar tus propias publicaciones.");
                    return;
                }

                opciones.hidden = !opciones.hidden;
                return;
            }

            if (accion === "editar") {
                if (tarjeta.dataset.propia !== "true") return;
                tarjeta.querySelector(".pub-opciones").hidden = true;
                abrirModal(tarjeta);
                return;
            }

            if (accion === "eliminar") {
                if (tarjeta.dataset.propia !== "true") return;

                if (!confirm("¿Deseas eliminar esta publicación de la pantalla?")) {
                    return;
                }

                tarjeta.remove();
                avisar("Publicación eliminada de la demostración.");
                filtrarPublicaciones();
                return;
            }

            
            if (accion === "like") {
                const activo = boton.getAttribute("aria-pressed") === "true";

                // Actualizar el estado de la reacción.
                boton.setAttribute("aria-pressed", String(!activo));

                boton.textContent = activo
                    ? "♡ Me gusta"
                    : "♥ Te gusta";

                // Recalcular las estadísticas de la tarjeta.
                const reaccionesActuales =
                    Number(tarjeta.dataset.likesBase) || 0;

                tarjeta.dataset.likesBase = String(
                    Math.max(0, reaccionesActuales + (activo ? -1 : 1))
                );

                actualizarEstadisticas(tarjeta);
                return;
            }


            if (accion === "comentar") {
                const panel = tarjeta.querySelector(".pub-comentarios");
                panel.hidden = !panel.hidden;

                if (!panel.hidden) {
                    panel.querySelector("input").focus();
                }
                return;
            }

            if (accion === "compartir") {
                const texto = tarjeta.querySelector(".pub-texto")
                    .textContent.trim();

                try {
                    if (navigator.clipboard && window.isSecureContext) {
                        await navigator.clipboard.writeText(texto);
                        avisar("Contenido copiado. Ya puedes compartirlo.");
                    } else {
                        avisar("Compartir: copia el texto de la publicación para enviarlo.");
                    }
                } catch {
                    avisar("Compartir: la publicación está lista para compartir.");
                }
            }
        });

        
        lista.addEventListener("submit", evento => {
            const formularioComentario = evento.target.closest(
                ".pub-form-comentario"
            );

            if (!formularioComentario) return;

            evento.preventDefault();

            const campo = formularioComentario.elements.comentario;
            const texto = campo.value.trim();

            if (!texto) {
                campo.focus();
                return;
            }

            const tarjeta = formularioComentario.closest(".pub-tarjeta");
            if (!tarjeta) return;

            const listaComentarios = tarjeta.querySelector(
                ".pub-comentarios-lista"
            );

            if (!listaComentarios) return;

            const comentario = crearElemento("div", "pub-comentario");

            const autor = crearElemento(
                "strong",
                "",
                "Docente Líder"
            );

            const contenido = document.createTextNode(" " + texto);

            comentario.append(autor, contenido);
            listaComentarios.append(comentario);

            formularioComentario.reset();

            actualizarEstadisticas(tarjeta);

            avisar("Comentario añadido en esta demostración.");
        });


        buscar.addEventListener("input", filtrarPublicaciones);

        function filtrarPublicaciones() {
            const consulta = buscar.value.trim().toLocaleLowerCase("es");

            let visibles = 0;

            lista.querySelectorAll(".pub-tarjeta").forEach(tarjeta => {
                const coincide = tarjeta.textContent
                    .toLocaleLowerCase("es")
                    .includes(consulta);

                tarjeta.hidden = !coincide;
                if (coincide) visibles++;
            });

            sinResultados.hidden = visibles !== 0;
        }

        // Los archivos de ejemplo no se descargan porque no existen físicamente.
        lista.addEventListener("click", evento => {
            const enlace = evento.target.closest("[data-archivo-demo]");
            if (!enlace) return;

            evento.preventDefault();
            avisar("Este archivo es ilustrativo y no está almacenado en el servidor.");
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciarPublicaciones);
    } else {
        iniciarPublicaciones();
    }
})();
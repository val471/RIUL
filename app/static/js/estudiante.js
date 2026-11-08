

// ICONOS (TRAZOS SVG)
const ICONOS = {
    home: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    clip: '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9zM9 12h6M9 16h4"/>',
    check: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    shield: '<path d="M5 4h14v8a7 7 0 0 1-14 0z"/>',
    folder: '<path d="M3 6h6l2 2h10v11H3z"/>',
    cal: '<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    mega: '<path d="M3 11v3l12 5V6z"/><path d="M15 9a3 3 0 0 1 0 6M7 14v5"/>',
    book: '<path d="M2 5h7a3 3 0 0 1 3 3v12a2 2 0 0 0-2-2H2zM22 5h-7a3 3 0 0 0-3 3v12a2 2 0 0 1 2-2h8z"/>',
    chart: '<rect x="4" y="12" width="4" height="8"/><rect x="10" y="4" width="4" height="16"/><rect x="16" y="9" width="4" height="11"/>',
    bell: '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4zM10 21h4"/>',
    out: '<path d="M9 4H5v16h4M16 8l4 4-4 4M20 12H9"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    heart: '<path d="M12 20s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 9c0 6-8 11-8 11z"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.5 7.2L4 20l1-4.5A8 8 0 1 1 21 12z"/>',
    share: '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.2 10.8l7.6-3.6M8.2 13.2l7.6 3.6"/>'
};

const svg = n =>
    '<svg class="s" viewBox="0 0 24 24" aria-hidden="true">' +
    (ICONOS[n] || '') + '</svg>';

const esc = t => String(t).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])
);

// CARGAR ICONOS
function cargarIconos(contenedor = document) {
    contenedor.querySelectorAll("[data-icon]").forEach(el => {
        const nombre = el.dataset.icon;

        if (ICONOS[nombre] && !el.querySelector("svg")) {
            el.insertAdjacentHTML("afterbegin",
                '<svg viewBox="0 0 24 24" aria-hidden="true">' +
                ICONOS[nombre] + '</svg>'
            );
        }
    });
}

cargarIconos();


// ---------- NAVEGACIÓN ----------
function mostrarModulo(id) {
    const modulo = document.getElementById(id);
    if (!modulo) return;

    document.querySelectorAll(".modulo").forEach(s => s.hidden = true);
    modulo.hidden = false;

    // CARGAR PERFIL
    if (id === "perfil" && !modulo.dataset.cargado) {
        fetch("/estudiante/perfil")
            .then(respuesta => {
                if (!respuesta.ok) throw new Error("Error al cargar perfil");
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
                inicializarPerfil();
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Mi perfil.</p>";
            });
    }

    // CARGAR SEMILLEROS
    if (id === "semillero" && !modulo.dataset.cargado) {
        fetch("/estudiante/semilleros")
            .then(respuesta => {
                if (!respuesta.ok) throw new Error("Error al cargar semilleros");
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Semilleros.</p>";
            });
    }

    // CARGAR EVENTOS
    if (id === "eventos" && !modulo.dataset.cargado) {
        fetch("/estudiante/eventos")
            .then(respuesta => {
                if (!respuesta.ok) throw new Error("Error al cargar eventos");
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
                filtrarEventos();
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Eventos.</p>";
            });
    }

    // CARGAR LOGROS
    if (id === "logros" && !modulo.dataset.cargado) {
        fetch("/estudiante/logros")
            .then(respuesta => {
                if (!respuesta.ok) throw new Error("Error al cargar logros");
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Mis logros.</p>";
            });
    }

    // CARGAR CONVOCATORIAS
    if (id === "convocatorias") {
        cargarConvocatorias(modulo);
    }

    // CARGAR PUBLICACIONES
    if (id === "publicaciones" && !modulo.dataset.cargado) {
        fetch("/estudiante/publicaciones")
            .then(respuesta => {
                if (!respuesta.ok) {
                    throw new Error("Error al cargar publicaciones");
                }
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
                inicializarPublicaciones();
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Publicaciones.</p>";
            });
    }

    // CARGAR RANKING
    if (id === "rankingestu" && !modulo.dataset.cargado) {
        fetch("/estudiante/rankingestu")
            .then(respuesta => {
                if (!respuesta.ok) {
                    throw new Error("Error al cargar ranking");
                }
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
                filtrarRanking();
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Ranking.</p>";
            });
    }

    // CARGAR HOJA DE VIDA
    if (id === "hoja-vida" && !modulo.dataset.cargado) {
        fetch("/estudiante/hoja-vida")
        .then(respuesta => {
            if (!respuesta.ok) {
                throw new Error("Error al cargar hoja de vida");
            }
            return respuesta.text();
        })
        .then(html => {
            modulo.innerHTML = html;
            modulo.dataset.cargado = "true";
            cargarIconos(modulo);
            cargarHojaVida();
        })
        .catch(() => {
            modulo.innerHTML = "<p>Error al cargar la hoja de vida.</p>";
        });

    // CARGAR LOGROS
    if (id === "logros" && !modulo.dataset.cargado) {
        fetch("/estudiante/logros")
            .then(respuesta => {
                if (!respuesta.ok) throw new Error("Error al cargar logros");
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Mis logros.</p>";
            });
    }
}
 
   /// BUSCAND A NEMO 

    document.querySelectorAll(".menu a[data-modulo]").forEach(a =>
        a.classList.toggle("activo", a.dataset.modulo === id)
    );

    const activo = document.querySelector('.menu a[data-modulo="' + id + '"]');

    document.getElementById("tituloModulo").textContent =
        activo
            ? activo.textContent.trim()
            : "Inicio";

    document.getElementById("sidebar").classList.remove("abierto");
    history.replaceState(null, "", "#" + id);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll(".menu a[data-modulo]").forEach(a =>
    a.addEventListener("click", e => {
        e.preventDefault();
        mostrarModulo(a.dataset.modulo);
    })
);

const permitidos = [
    "inicio", "perfil", "semillero", "proyectos", "hoja-vida",
    "logros", "eventos", "convocatorias", "publicaciones",
    "rankingestu"
];

const inicial = location.hash.substring(1);
mostrarModulo(permitidos.includes(inicial) ? inicial : "inicio");


// ---------- SEMILLEROS ----------
const formSemillero = document.getElementById("formSemillero");

if (formSemillero) {
    formSemillero.addEventListener("submit", function(e) {
        e.preventDefault();

        const mensaje = document.getElementById("mensajeSemillero");

        if (mensaje) {
            mensaje.textContent =
                "Formulario completado. La solicitud aún no se ha enviado al docente líder.";
        }
    });
}

// BUSCAR SEMILLEROS
document.addEventListener("input", e => {
    if (e.target.id !== "buscarSemillero") return;

    const texto = e.target.value.toLowerCase().trim();
    const tarjetas = document.querySelectorAll("#listaSemilleros .semillero-card");

    tarjetas.forEach(tarjeta => {
        tarjeta.hidden = !tarjeta.textContent.toLowerCase().includes(texto);
    });
});


// ---------- EVENTOS ----------
function filtrarEventos() {
    const buscador = document.getElementById("buscarEvento");
    const filtro = document.getElementById("filtroEvento");
    const lista = document.getElementById("listaEventos");

    if (!buscador || !filtro || !lista) return;

    const texto = buscador.value.toLowerCase().trim();
    const estadoSeleccionado = filtro.value;

    lista.querySelectorAll(".evento-card").forEach(evento => {
        const nombre = evento.querySelector("h3")?.textContent.toLowerCase() || "";
        const estado = evento.querySelector(".evento-estado");

        const estadoEvento = estado?.classList.contains("abierto")
            ? "abierto"
            : "cerrado";

        evento.hidden = !(
            nombre.includes(texto) &&
            (estadoSeleccionado === "todos" || estadoEvento === estadoSeleccionado)
        );
    });
}

document.addEventListener("input", e => {
    if (e.target.id === "buscarEvento") {
        filtrarEventos();
    }
});

document.addEventListener("change", e => {
    if (e.target.id === "filtroEvento") {
        filtrarEventos();
    }
});


// ---------- CONVOCATORIAS ----------

function cargarConvocatorias(modulo) {
    if (modulo.dataset.cargado) return;

    fetch("/estudiante/convocatorias")
        .then(respuesta => {
            if (!respuesta.ok) {
                throw new Error("Error al cargar convocatorias");
            }
            return respuesta.text();
        })
        .then(html => {
            modulo.innerHTML = html;
            modulo.dataset.cargado = "true";
            cargarIconos(modulo);
            filtrarConvocatorias();
        })
        .catch(() => {
            modulo.innerHTML = "<p>Error al cargar Convocatorias.</p>";
        });
}

function filtrarConvocatorias() {
    const buscador = document.getElementById("buscarConvocatoria");
    const filtro = document.getElementById("filtroConvocatoria");
    const lista = document.getElementById("listaConvocatorias");

    if (!buscador || !filtro || !lista) return;

    const texto = buscador.value.toLowerCase().trim();
    const estadoSeleccionado = filtro.value;

    lista.querySelectorAll(".convocatoria-card").forEach(convocatoria => {
        const nombre = convocatoria.querySelector("h3")?.textContent.toLowerCase() || "";
        const estado = convocatoria.querySelector(".convocatoria-estado");

        const estadoConvocatoria = estado?.classList.contains("abierta")
            ? "abierta"
            : "cerrada";

        convocatoria.hidden = !(
            nombre.includes(texto) &&
            (estadoSeleccionado === "todos" ||
             estadoConvocatoria === estadoSeleccionado)
        );
    });
}

document.addEventListener("input", e => {
    if (e.target.id === "buscarConvocatoria") {
        filtrarConvocatorias();
    }
});

document.addEventListener("change", e => {
    if (e.target.id === "filtroConvocatoria") {
        filtrarConvocatorias();
    }
});


// ---------- LOGROS ----------
const formLogro = document.getElementById("formLogro");

if (formLogro) {
    formLogro.addEventListener("submit", function(e) {
        e.preventDefault();

        const mensaje = document.getElementById("mensajeLogro");

        if (mensaje) {
            mensaje.textContent =
                "Formulario completado. La evidencia todavía no se ha guardado ni enviado para validación.";
        }
    });
}


// ---------- HOJA DE VIDA ----------

function mostrarDatosHV(contenedor, datos) {
    const elemento = document.getElementById(contenedor);

    if (!elemento) return;

    if (!datos || datos.length === 0) {
        elemento.innerHTML = "<p>No hay información registrada.</p>";
        return;
    }

    elemento.innerHTML = datos.map(dato => `
        <div class="item-hv">
            <h4>${esc(dato.titulo || dato.nombre || "Sin título")}</h4>
            <p>${esc(dato.detalle || dato.descripcion || "")}</p>
        </div>
    `).join("");
}

function cargarHojaVida() {
    mostrarDatosHV("hvPerfil", []);
    mostrarDatosHV("hvSemilleros", []);
    mostrarDatosHV("hvLogros", []);
    mostrarDatosHV("hvEventos", []);
    mostrarDatosHV("hvPublicaciones", []);
    mostrarDatosHV("hvProyectos", []);
    mostrarDatosHV("hvInsignias", []);
}

function descargarHojaVida() {
    const mensaje = document.getElementById("mensajeHojaVida");

    if (mensaje) {
        mensaje.textContent =
            "La descarga del PDF estará disponible cuando conectemos esta sección con Flask.";
    }
}


// ---------- PERFIL ----------
function inicializarPerfil() {
    const msgPerfil = document.getElementById("mensajePerfil");
    const formPerfil = document.getElementById("formPerfil");

    if (formPerfil) {
        formPerfil.addEventListener("submit", e => {
            e.preventDefault();

            const clave = document.getElementById("clave").value;

            if (clave && clave.length < 8) {
                msgPerfil.textContent =
                    "La contraseña debe tener mínimo 8 caracteres.";
                return;
            }

            msgPerfil.textContent =
                "Cambios validados en el navegador. Aún no se guardan en la base de datos.";
        });
    }

    const btnSolicitar = document.getElementById("btnSolicitar");

    if (btnSolicitar) {
        btnSolicitar.addEventListener("click", () => {
            const b = document.getElementById("bloqueSolicitud");
            b.hidden = !b.hidden;

            if (!b.hidden) {
                document.getElementById("motivoPerfil").focus();
            }
        });
    }

    const enviarSolicitud = document.getElementById("enviarSolicitud");

    if (enviarSolicitud) {
        enviarSolicitud.addEventListener("click", () => {
            if (!document.getElementById("motivoPerfil").value.trim()) {
                msgPerfil.textContent = "Debes explicar el motivo del cambio.";
                return;
            }

            document.getElementById("estadoPerfil").textContent =
                "Pendiente de aprobación (demostración local).";

            msgPerfil.textContent =
                "Solicitud validada. Todavía no se envió al administrador.";
        });
    }

    const fotoPerfil = document.getElementById("fotoPerfil");

    if (fotoPerfil) {
        fotoPerfil.addEventListener("change", e => {
            if (e.target.files[0]) {
                msgPerfil.textContent =
                    "Foto seleccionada: " + e.target.files[0].name;
            }
        });
    }
}


// ---------- RANKING ----------
const ranking = [
    { n: "Patricia Herrera", s: "Biotecnología Aplicada", xp: 1245, e: 5 },
    { n: "Ricardo Solano", s: "Derecho Digital", xp: 1090, e: 5 },
    { n: "Laura Gómez", s: "Tecnología e Innovación", xp: 980, e: 4 },
    { n: "Andrés Martínez", s: "Tecnología e Innovación", xp: 675, e: 3, yo: true },
    { n: "María Ospina", s: "Salud Pública", xp: 620, e: 3 },
    { n: "Felipe Castro", s: "Finanzas e Innovación", xp: 575, e: 3 }
];

function filtrarRanking() {
    const buscador = document.getElementById("buscarRanking");
    const lista = document.getElementById("listaRanking");

    if (!buscador || !lista) return;

    const q = buscador.value.trim().toLowerCase();

    const filas = ranking.map((r, i) => ({ ...r, pos: i + 1 }))
        .filter(r => r.n.toLowerCase().includes(q) || r.s.toLowerCase().includes(q));

    lista.innerHTML =
        '<div class="fila cabeza"><span>Posición</span><span>Investigador</span><span>Semillero</span><span>XP</span><span>Nivel</span></div>' +
        (filas.length ? filas.map(r =>
            '<div class="fila' + (r.yo ? ' yo' : '') + '"><span class="pos">#' + r.pos +
            '</span><span class="nom">' + esc(r.n) +
            '</span><span class="sem">' + esc(r.s) +
            '</span><span class="xpv">' + r.xp.toLocaleString("es-CO") +
            ' XP</span><span class="niv" aria-label="' + r.e + ' estrellas">' +
            "★".repeat(r.e) + '</span></div>'
        ).join("") : '<p class="vacio">No se encontraron resultados.</p>');
}

// BUSCAR RANKING
document.addEventListener("input", e => {
    if (e.target.id === "buscarRanking") {
        filtrarRanking();
    }
});


// ---------- PUBLICACIONES ----------
const pubs = [
    {
        a: "Dra. Laura Gómez", i: "LG",
        m: "Hace 2 horas · Publicación académica · 5 XP",
        x: "Nuestro semillero presentó avances del proyecto de analítica educativa. Gracias a todo el equipo por su trabajo riguroso.",
        f: "memorias_congreso.pdf", r: 34, c: 8, v: 186, like: false, mia: false
    },
    {
        a: "Andrés Martínez", i: "AM",
        m: "Ayer · Publicación académica",
        x: "Terminé la revisión de literatura de mi proyecto. Comparto el resumen para recibir comentarios.",
        f: "", r: 12, c: 3, v: 74, like: false, mia: true
    }
];

function pintarPubs() {
    const buscador = document.getElementById("buscarPub");
    const lista = document.getElementById("listaPubs");

    if (!buscador || !lista) return;

    const q = buscador.value.trim().toLowerCase();

    const resultados = pubs.map((p, i) => ({ p, i }))
        .filter(({ p }) => (p.a + " " + p.x).toLowerCase().includes(q));

    lista.innerHTML = resultados.length
        ? resultados.map(({ p, i }) =>
            '<article class="tarjeta pub">' +
            '<div class="pub-cab"><span class="pub-avatar">' + p.i + '</span>' +
            '<div><b>' + esc(p.a) + '</b><small>' + esc(p.m) + '</small></div>' +
            (p.mia
                ? '<div class="acc"><button class="link-accion" data-accion="editar" data-i="' + i + '">Editar</button>' +
                  '<button class="link-accion" data-accion="eliminar" data-i="' + i + '">Eliminar</button></div>'
                : '') +
            '</div><p class="pub-texto">' + esc(p.x) + '</p>' +
            (p.f ? '<div class="pub-archivo">' + svg("book") + '<span>' + esc(p.f) + '</span></div>' : '') +
            '<div class="pub-stats"><span>' + p.r + ' reacciones · ' + p.c + ' comentarios</span>' +
            '<span class="vistas">' + svg("eye") + p.v + ' vistas</span></div>' +
            '<div class="pub-botones">' +
            '<button type="button" class="' + (p.like ? 'activo' : '') + '" data-accion="like" data-i="' + i + '">' + svg("heart") + 'Me gusta</button>' +
            '<button type="button" data-accion="comentar" data-i="' + i + '">' + svg("chat") + 'Comentar</button>' +
            '<button type="button" data-accion="compartir" data-i="' + i + '">' + svg("share") + 'Compartir</button>' +
            '</div></article>'
        ).join("")
        : '<p class="vacio">No se encontraron publicaciones.</p>';
}

function inicializarPublicaciones() {
    const buscador = document.getElementById("buscarPub");
    const lista = document.getElementById("listaPubs");
    const btnPublicar = document.getElementById("btnPublicar");
    const formPub = document.getElementById("formPub");

    if (!lista) return;

    pintarPubs();

    if (buscador) {
        buscador.addEventListener("input", pintarPubs);
    }

    lista.addEventListener("click", e => {
        const b = e.target.closest("[data-accion]");
        if (!b) return;

        const i = Number(b.dataset.i);
        const p = pubs[i];
        if (!p) return;

        const ac = b.dataset.accion;

        if (ac === "like") {
            p.like = !p.like;
            p.r += p.like ? 1 : -1;
        } else if (ac === "comentar") {
            const t = prompt("Escribe tu comentario:");
            if (t && t.trim()) p.c++;
        } else if (ac === "compartir") {
            navigator.clipboard?.writeText(location.href + "#publicaciones");
            alert("Enlace copiado.");
        } else if (ac === "editar") {
            const t = prompt("Editar publicación:", p.x);
            if (t && t.trim()) p.x = t.trim();
        } else if (ac === "eliminar") {
            if (confirm("¿Eliminar esta publicación?")) pubs.splice(i, 1);
        }

        pintarPubs();
    });

    if (btnPublicar && formPub) {
        btnPublicar.addEventListener("click", () => {
            formPub.hidden = !formPub.hidden;
        });

        formPub.addEventListener("submit", e => {
            e.preventDefault();

            const texto = document.getElementById("pubTexto");
            const archivo = document.getElementById("pubArchivo");
            const arch = archivo.files[0];

            if (!texto.value.trim()) return;

            pubs.unshift({
                a: "Andrés Martínez",
                i: "AM",
                m: "Hace un momento · Publicación académica",
                x: texto.value.trim(),
                f: arch ? arch.name : "",
                r: 0, c: 0, v: 0, like: false, mia: true
            });

            e.target.reset();
            e.target.hidden = true;
            pintarPubs();
        });
    }

    // ---------- NOTIFICACIONES ----------
function inicializarNotificaciones() {
    const boton = document.getElementById("marcarTodasLeidas");
    const lista = document.getElementById("listaNotificaciones");
    const contador = document.getElementById("contadorNotificaciones");

    if (!boton || !lista || !contador) return;

    function actualizarContador() {
        const pendientes = lista.querySelectorAll(".notificacion.no-leida").length;

        contador.textContent = pendientes === 1
            ? "1 notificacion sin leer."
            : `${pendientes} notificaciones sin leer.`;
    }

    boton.addEventListener("click", () => {
        lista.querySelectorAll(".notificacion").forEach(notificacion => {
            notificacion.classList.remove("no-leida");
            notificacion.classList.add("leida");
        });

        actualizarContador();
    });

    actualizarContador();
}

}

// VENTANA DE CERRAR SESION
const modalCerrarSesion = document.getElementById("modalCerrarSesion");
const cancelarCerrarSesion = document.getElementById("cancelarCerrarSesion");
const confirmarCerrarSesion = document.getElementById("confirmarCerrarSesion");

const enlaceCerrarSesion = document.querySelector(".cerrar-sesion");
console.log("Enlace:", enlaceCerrarSesion);
console.log("Modal:", modalCerrarSesion);

if (enlaceCerrarSesion && modalCerrarSesion) {
    enlaceCerrarSesion.addEventListener("click", function (e) {
        e.preventDefault();
        modalCerrarSesion.hidden = false;
    });
}

if (cancelarCerrarSesion) {
    cancelarCerrarSesion.addEventListener("click", function () {
        modalCerrarSesion.hidden = true;
    });
}

if (confirmarCerrarSesion) {
    confirmarCerrarSesion.addEventListener("click", function () {
        window.location.href = "/cerrar-sesion";
    });
}

// ==============================
// PANEL DE NOTIFICACIONES
// ==============================

const btnNotificaciones = document.getElementById("btnNotificaciones");
const panelNotificaciones = document.getElementById("panelNotificaciones");
const marcarTodasLeidas = document.getElementById("marcarTodasLeidas");
const badgeNotif = document.getElementById("badgeNotif");

// ACTUALIZAR CONTADOR
function actualizarBadgeNotificaciones() {
    const pendientes = document.querySelectorAll(
        "#listaNotificaciones .notificacion.no-leida"
    ).length;

    if (badgeNotif) {
        badgeNotif.textContent = pendientes;
        badgeNotif.hidden = pendientes === 0;
    }
}

// ABRIR Y CERRAR PANEL
if (btnNotificaciones && panelNotificaciones) {
    btnNotificaciones.addEventListener("click", function(e) {
        e.stopPropagation();

        panelNotificaciones.hidden = !panelNotificaciones.hidden;

        btnNotificaciones.setAttribute(
            "aria-expanded",
            String(!panelNotificaciones.hidden)
        );
    });

    // CERRAR AL HACER CLIC FUERA
    document.addEventListener("click", function(e) {
        if (
            !panelNotificaciones.contains(e.target) &&
            !btnNotificaciones.contains(e.target)
        ) {
            panelNotificaciones.hidden = true;
            btnNotificaciones.setAttribute("aria-expanded", "false");
        }
    });
}

// MARCAR TODAS COMO LEIDAS
if (marcarTodasLeidas) {
    marcarTodasLeidas.addEventListener("click", function() {
        document.querySelectorAll(
            "#listaNotificaciones .notificacion"
        ).forEach(notificacion => {
            notificacion.classList.remove("no-leida");
            notificacion.classList.add("leida");
        });

        actualizarBadgeNotificaciones();
    });
}

// MOSTRAR CONTADOR INICIAL
actualizarBadgeNotificaciones();

// MOSTRAR DATOS INICIALES
cargarHojaVida();
filtrarRanking();
pintarPubs();
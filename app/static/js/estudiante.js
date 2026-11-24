

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
                cargarSemillerosReales();   
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

    // CARGAR  CONVOCATORIAS
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

    // CARGAR MIS PROYECTOS
    if (id === "proyectos" && !modulo.dataset.cargado) {
        fetch("/estudiante/proyectos")
            .then(respuesta => {
                if (!respuesta.ok) {
                    throw new Error("Error al cargar proyectos");
                }
                return respuesta.text();
            })
            .then(html => {
                modulo.innerHTML = html;
                modulo.dataset.cargado = "true";
                cargarIconos(modulo);
                cargarMisProyectos();
            })
            .catch(() => {
                modulo.innerHTML = "<p>Error al cargar Mis proyectos.</p>";
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
 
   // BUSCAND A NEMO 

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

// ---------- SEMILLEROS REALES ----------
async function cargarSemillerosReales() {
    const lista = document.getElementById("listaSemilleros");
    if (!lista) return;

    lista.innerHTML = "<p>Cargando semilleros...</p>";

    try {
        const respuesta = await fetch("/estudiante/api/semilleros");
        if (!respuesta.ok) throw new Error("Error al cargar semilleros");

        const semilleros = await respuesta.json();

        if (semilleros.length === 0) {
            lista.innerHTML = "<p>Aún no hay semilleros activos.</p>";
            return;
        }

        lista.innerHTML = semilleros.map(s => {
            const sinCupo = s.integrantes >= s.cupo_maximo;
let botonPrincipal;

if (s.mi_solicitud === "PENDIENTE") {
    botonPrincipal =
        '<button type="button" class="boton boton-principal" disabled>' +
        'Solicitud pendiente</button>';

} else if (s.mi_solicitud === "ACEPTADA") {
    botonPrincipal =
        '<button type="button" class="boton boton-principal" disabled>' +
        'Solicitud aceptada</button>';

} else if (!s.es_mi_facultad) {
    botonPrincipal =
        '<button type="button" class="boton boton-principal" disabled>' +
        'Otra facultad</button>';

} else if (sinCupo) {
    botonPrincipal =
        '<button type="button" class="boton boton-principal" disabled>' +
        'Sin cupo</button>';

} else {
    botonPrincipal =
        '<button type="button" class="boton boton-principal btn-solicitar" ' +
        'data-id="' + s.id + '">Solicitar vinculación</button>';
}
            return (
                '<article class="semillero-card">' +
                    '<div class="semillero-info">' +
                        '<span class="semillero-categoria">' +
                            esc(s.linea || "SIN LÍNEA DEFINIDA") + "</span>" +
                        "<h3>" + esc(s.nombre) + "</h3>" +
                        "<p>" + esc(s.descripcion || "Sin descripción.") + "</p>" +
                        '<div class="semillero-datos">' +
                            "<span>" + esc(s.facultad) + "</span>" +
                            "<span>" + s.integrantes + " de " + s.cupo_maximo +
                            " integrantes</span>" +
                        "</div>" +
                        '<div class="semillero-acciones">' +
                            botonPrincipal +
                            '<button type="button" class="boton btn-seguir" data-id="' + s.id + '">Seguir</button>' +
                        "</div>" +
                    "</div>" +
                "</article>"
            );
        }).join("");

    } catch (error) {
        lista.innerHTML = "<p>No fue posible cargar los semilleros.</p>";
    }
}
//BOTON SE SEGUIR
document.addEventListener("click", async e => {
    const boton = e.target.closest(".btn-seguir");
    if (!boton) return;

    boton.disabled = true;
    boton.textContent = "Siguiendo...";

    try {
        const respuesta = await fetch(
            "/estudiante/api/semilleros/" + boton.dataset.id + "/seguir",
            { method: "POST" }
        );

        const resultado = await respuesta.json();

        console.log("RESPUESTA DE SEGUIR:", respuesta.status, resultado);

        if (!respuesta.ok) {
            boton.disabled = false;
            boton.textContent = "Seguir";
            console.error("Error al seguir:", resultado.mensaje);
            return;
        }

        boton.textContent = "Siguiendo";

    } catch (error) {
        console.error("Error al seguir semillero:", error);
        boton.disabled = false;
        boton.textContent = "Seguir";
    }
});
// ---------- SOLICITAR VINCULACIÓN ----------
document.addEventListener("click", async e => {
    const boton = e.target.closest(".btn-solicitar");
    if (!boton) return;

    boton.disabled = true;
    boton.textContent = "Enviando...";

    try {
        const respuesta = await fetch(
            "/estudiante/api/semilleros/" + boton.dataset.id + "/solicitar",
            { method: "POST" }
        );
        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.mensaje || "No fue posible enviar la solicitud.");
            } else {
              alert(resultado.mensaje || "Solicitud enviada correctamente.");
         }

        
    } catch (error) {
        alert("No fue posible enviar la solicitud.");
    }

    // Se vuelve a dibujar la lista para mostrar el estado actualizado
    cargarSemillerosReales();
});

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
// ---------- CARGAR EVENTOS REALES ----------
async function cargarEventos() {

    const lista = document.getElementById("listaEventos");

    if (!lista) return;

    lista.innerHTML = "<p>Cargando eventos...</p>";

    try {
        const respuesta = await fetch("/estudiante/api/eventos");

        if (!respuesta.ok) {
            throw new Error("Error al consultar eventos");
        }

        const eventos = await respuesta.json();

        if (eventos.length === 0) {
            lista.innerHTML = "<p>No hay eventos disponibles.</p>";
            return;
        }

        lista.innerHTML = eventos.map(evento => `
            <article class="evento-card">
                <div class="evento-icono">
                    <span data-icon="cal"></span>
                </div>

                <div class="evento-info">
                    <h3>${esc(evento.nombre)}</h3>
                    <p>
                        Cierre: ${evento.fecha_cierre
                            ? esc(evento.fecha_cierre)
                            : "Sin fecha de cierre"}
                        · Modalidad: ${esc(evento.modalidad)}
                    </p>
                </div>

                <div class="evento-acciones">
                    <span class="evento-estado ${evento.estado}">
                        ${evento.estado === "abierto" ? "Abierto" : "Cerrado"}
                    </span>
                </div>
            </article>
        `).join("");

        cargarIconos(lista);
        cargarEventos();

    } catch (error) {
        console.error("Error al cargar eventos:", error);
        lista.innerHTML = "<p>No fue posible cargar los eventos.</p>";
    }
}
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

document.addEventListener("click", function(e) {

    if (e.target.closest("#btnMostrarFormulario")) {
        const formulario = document.getElementById("formRegistrarLogro");

        if (formulario) {
            formulario.hidden = false;
        }
    }

    if (e.target.closest("#btnCancelarLogro")) {
        const formulario = document.getElementById("formRegistrarLogro");

        if (formulario) {
            formulario.reset();
            formulario.hidden = true;
        }
    }

});

document.addEventListener("submit", async function(e) {

    if (e.target.id !== "formRegistrarLogro") return;

    e.preventDefault();

    const formulario = e.target;
    const mensaje = document.getElementById("mensajeLogro");
    const boton = formulario.querySelector('[type="submit"]');

    boton.disabled = true;
    boton.textContent = "Enviando...";

    try {

        const respuesta = await fetch(formulario.action, {
            method: "POST",
            body: new FormData(formulario)
        });

        const resultado = await respuesta.json();

        if (!respuesta.ok || !resultado.exito) {
            throw new Error(resultado.mensaje || "No se pudo registrar el logro.");
        }

        
        mensaje.textContent = resultado.mensaje;
        formulario.reset();
        formulario.hidden = true;

// Actualizar la lista de logros
const respuestaLista = await fetch("/estudiante/logros");

if (respuestaLista.ok) {
    const html = await respuestaLista.text();
    const documento = new DOMParser().parseFromString(html, "text/html");

    const nuevaLista = documento.getElementById("listaLogros");
    const listaActual = document.getElementById("listaLogros");

    if (nuevaLista && listaActual) {
        listaActual.innerHTML = nuevaLista.innerHTML;
    } 
    }  

    } catch (error) {

        mensaje.textContent = error.message;

    } finally {

        boton.disabled = false;
        boton.textContent = "Enviar logro";

    }

});

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
    fetch("/estudiante/hoja-vida/datos")
        .then(respuesta => {
            if (!respuesta.ok) {
                throw new Error("Error al consultar la hoja de vida");
            }
            return respuesta.json();
        })
        .then(datos => {
            mostrarDatosHV("hvLogros", datos.logros);
            // DATOS PRINCIPALES
           const perfil = datos.perfil || {};

         document.getElementById("hvNombre").textContent =
         perfil.nombre || "Nombre del estudiante";

         document.getElementById("hvPrograma").textContent =
         perfil.programa || "Programa académico";

         document.getElementById("hvSemestre").textContent =
         perfil.semestre ? `Semestre ${perfil.semestre}` : "Semestre";

         document.getElementById("hvExperiencia").textContent =
         `${perfil.xp_total || 0} XP`;

         // NIVEL DEL INVESTIGADOR
         document.getElementById("hvNivel").textContent =
         perfil.nivel || "Nivel no asignado";

         // ESTRELLAS DEL NIVEL
         const estrellas = Number(perfil.estrellas) || 0;

         document.querySelector(".hv-estrellas").textContent =
         "★".repeat(estrellas) + "☆".repeat(Math.max(0, 5 - estrellas));

          // FOTO E INICIALES
         const avatar = document.getElementById("hvAvatar");
         const foto = document.getElementById("hvFoto");
         const iniciales = document.getElementById("hvIniciales");

         const nombres = (perfil.nombre || "AM").trim().split(/\s+/);

         iniciales.textContent = nombres.length > 1
         ? nombres[0][0] + nombres[nombres.length - 1][0]
         : nombres[0].substring(0, 2);

         if (perfil.foto_perfil) {
         foto.src = perfil.foto_perfil;
         foto.style.display = "block";
         iniciales.style.display = "none";
         } else {
         foto.style.display = "none";
         iniciales.style.display = "block";
         }
         // INFORMACION DEL ESTUDIANTE
         document.getElementById("hvPerfil").innerHTML = `
         <div class="item-hv">
         <h4>Correo institucional</h4>
         <p>${esc(perfil.correo || "No registrado")}</p>
         </div>

         <div class="item-hv">
         <h4>Teléfono</h4>
         <p>${esc(perfil.telefono || "No registrado")}</p>
         </div>

         <div class="item-hv">
         <h4>Fecha de nacimiento</h4>
         <p>${esc(perfil.fecha_nacimiento || "No registrada")}</p>
         </div>
         `;
         // SEMILLEROS
         mostrarDatosHV("hvSemilleros", (datos.semilleros || []).map(s => ({
         titulo: s.nombre,
         detalle: `${s.descripcion || "Sin descripción"} | Línea: ${s.linea_investigacion || "No especificada"}`
         })));
         // EVENTOS
         mostrarDatosHV("hvEventos", (datos.eventos || []).map(e => ({
         titulo: e.nombre,
         detalle: `${e.tipo_participacion} | ${e.lugar || "Lugar no especificado"} | ${e.fecha || "Fecha no disponible"}`
         })));
         // PUBLICACIONES
         mostrarDatosHV("hvPublicaciones", (datos.publicaciones || []).map(p => ({
         titulo: p.categoria || p.tipo_publicacion || "Publicación académica",
         detalle: `${p.contenido} | ${p.fecha_publicacion || "Fecha no disponible"}`
         })));
         // PROYECTOS
         mostrarDatosHV("hvProyectos", (datos.proyectos || []).map(p => ({
         titulo: p.titulo,
         detalle: `${p.descripcion || "Sin descripción"} | Semillero: ${p.semillero} | Estado: ${p.estado} | Inicio: ${p.fecha_inicio}`
         })));
         // INSIGNIAS
         mostrarDatosHV("hvInsignias", (datos.insignias || []).map(i => ({
         titulo: i.nombre,
         detalle: `${i.descripcion || "Sin descripción"} | Grado: ${i.grado || "No especificado"} | Tipo: ${i.tipo || "No especificado"} | Obtenida: ${i.fecha_obtencion || "Fecha no disponible"}`
         })));
        })
        .catch(error => {
            console.error("Error al cargar hoja de vida:", error);
            document.getElementById("hvLogros").innerHTML =
                "<p>Error al consultar los logros.</p>";
        });
}

function descargarHojaVida() {
    window.print();
}





// ---------- PERFIL ----------

function inicializarPerfil() {

    const foto = document.getElementById("fotoPerfil");
    const cambiarFoto = document.getElementById("cambiarFoto");
    const guardarPerfil = document.getElementById("guardarPerfil");

    // ELEMENTOS DE SOLICITUD
    const solicitarCambio = document.getElementById("solicitarCambio");
    const modalSolicitud = document.getElementById("modalSolicitud");
    const cerrarModal = document.getElementById("cerrarModalSolicitud");
    const cancelarSolicitud = document.getElementById("cancelarSolicitud");
    const enviarSolicitud = document.getElementById("enviarSolicitud");

    // ELEMENTOS DE NOTIFICACION
    const notificacionPerfil = document.getElementById("notificacionPerfil");
    const cerrarNotificacion = document.getElementById("cerrarNotificacion");
    const tituloNotificacion = document.getElementById("tituloNotificacion");
    const mensajeNotificacion = document.getElementById("mensajeNotificacion");
    const iconoNotificacion = document.getElementById("iconoNotificacion");
    const errorSolicitud = document.getElementById("errorSolicitud");
    const campoSolicitud = document.getElementById("campoSolicitud");
    const campoValorSolicitud = document.getElementById("campoValorSolicitud");
    const campoFotoSolicitud = document.getElementById("campoFotoSolicitud");
    const archivoFotoSolicitud = document.getElementById("archivoFotoSolicitud");

    // FUNCION PARA MOSTRAR NOTIFICACION
    
    // CERRAR NOTIFICACION
    if (cerrarNotificacion && notificacionPerfil) {
        cerrarNotificacion.addEventListener("click", function () {
            notificacionPerfil.hidden = true;
        });
    }
        // FUNCION PARA MOSTRAR NOTIFICACION
    function mostrarNotificacion(titulo, mensaje, tipo) {
        if (tituloNotificacion && mensajeNotificacion && notificacionPerfil) {
            tituloNotificacion.textContent = titulo;
            mensajeNotificacion.textContent = mensaje;

            if (iconoNotificacion) {
                const esError = tipo === "error";
                iconoNotificacion.textContent = esError ? "✕" : "✓";
                iconoNotificacion.classList.toggle("error", esError);
            }

            notificacionPerfil.hidden = false;
        }
    }
    // MOSTRAR FOTO SELECCIONADA
    if (cambiarFoto && foto) {
        cambiarFoto.addEventListener("change", function () {

            const archivo = this.files[0];

            if (!archivo) return;

            if (!archivo.type.startsWith("image/")) {
                alert("Selecciona una imagen válida.");
                this.value = "";
                return;
            }

            foto.src = URL.createObjectURL(archivo);
        });
    }

    // ABRIR MODAL DE SOLICITUD
    if (solicitarCambio && modalSolicitud) {
        solicitarCambio.addEventListener("click", function () {
            modalSolicitud.hidden = false;
        });
    }

    // CERRAR MODAL
    if (cerrarModal && modalSolicitud) {
        cerrarModal.addEventListener("click", function () {
            modalSolicitud.hidden = true;
        });
    }

    if (cancelarSolicitud && modalSolicitud) {
        cancelarSolicitud.addEventListener("click", function () {
            modalSolicitud.hidden = true;
        });
    }


        // MOSTRAR CAMPO DE FOTO CUANDO SE ELIGE "FOTO DE PERFIL"
    if (campoSolicitud) {
        campoSolicitud.addEventListener("change", function () {
            const esFoto = campoSolicitud.value === "foto_perfil";

            if (campoValorSolicitud) {
                campoValorSolicitud.hidden = esFoto;
            }

            if (campoFotoSolicitud) {
                campoFotoSolicitud.hidden = !esFoto;
            }
        });
    }

    // ENVIAR SOLICITUD DE FOTO
    async function enviarSolicitudFoto(descripcion) {

        const archivo = archivoFotoSolicitud && archivoFotoSolicitud.files[0];

        if (!archivo || !descripcion) {
            if (errorSolicitud) {
                errorSolicitud.textContent =
                    "Selecciona la nueva foto y explica el motivo.";
                errorSolicitud.hidden = false;
            }
            return;
        }

        enviarSolicitud.disabled = true;

        try {
            const datos = new FormData();
            datos.append("foto", archivo);
            datos.append("descripcion", descripcion);

            const respuesta = await fetch("/estudiante/api/perfil/solicitud-foto", {
                method: "POST",
                body: datos
            });

            const resultado = await respuesta.json();

            modalSolicitud.hidden = true;

            if (!respuesta.ok) {
                mostrarNotificacion(
                    "No se pudo enviar",
                    resultado.mensaje || "No fue posible enviar la solicitud.",
                    "error"
                );
                return;
            }

            archivoFotoSolicitud.value = "";
            document.getElementById("descripcionSolicitud").value = "";

            mostrarNotificacion("¡Solicitud enviada!", resultado.mensaje);

        } catch (error) {
            console.error("Error al enviar la foto:", error);
            modalSolicitud.hidden = true;
            mostrarNotificacion(
                "Sin conexión",
                "No fue posible conectar con el servidor.",
                "error"
            );

        } finally {
            enviarSolicitud.disabled = false;
        }
    }

    // ENVIAR SOLICITUD A FLASK
    if (enviarSolicitud) {
        enviarSolicitud.addEventListener("click", async function () {

            const campo = document.getElementById("campoSolicitud").value;
            const valorNuevo = document.getElementById("valorNuevoSolicitud").value.trim();
            const descripcion = document.getElementById("descripcionSolicitud").value.trim();

            if (errorSolicitud) {
                errorSolicitud.hidden = true;
            }
            
            if (campo === "foto_perfil") {
                await enviarSolicitudFoto(descripcion);
                return;
            }

            if (!campo || !valorNuevo || !descripcion) {
                if (errorSolicitud) {
                    errorSolicitud.textContent = "Completa todos los campos de la solicitud.";
                    errorSolicitud.hidden = false;
                }
                return;
            }

            enviarSolicitud.disabled = true;

            try {
                const respuesta = await fetch("/estudiante/api/perfil/solicitud", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        campo: campo,
                        valor_nuevo: valorNuevo,
                        descripcion: descripcion
                    })
                });

                const resultado = await respuesta.json();

                modalSolicitud.hidden = true;

                if (!respuesta.ok) {
                    mostrarNotificacion(
                        "No se pudo enviar",
                        resultado.mensaje || "No fue posible enviar la solicitud.",
                        "error"
                    );
                    return;
                }

                document.getElementById("valorNuevoSolicitud").value = ""; 
                document.getElementById("descripcionSolicitud").value = ""; 

                mostrarNotificacion(
                    "¡Solicitud enviada!",
                    resultado.mensaje
                );

            } catch (error) {
                console.error("Error al enviar solicitud:", error);
                modalSolicitud.hidden = true;
                mostrarNotificacion(
                    "Sin conexión",
                    "No fue posible conectar con el servidor.",
                    "error"
                );

            } finally {
                enviarSolicitud.disabled = false;
            }
        });
    }

    // CAMBIAR CONTRASEÑA
    if (guardarPerfil) {
        guardarPerfil.addEventListener("click", async function () {

            const actual = document.getElementById("contrasenaActual").value;
            const nueva = document.getElementById("nuevaContrasena").value;
            const confirmar = document.getElementById("confirmarContrasena").value;

            if (!actual || !nueva || !confirmar) {
                alert("Completa los tres campos de contraseña.");
                return;
            }

            if (nueva.length < 8) {
                alert("La nueva contraseña debe tener mínimo 8 caracteres.");
                return;
            }

            if (nueva !== confirmar) {
                alert("Las contraseñas no coinciden.");
                return;
            }

            guardarPerfil.disabled = true;

            try {
                const respuesta = await fetch("/estudiante/api/perfil/contrasena", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        actual: actual,
                        nueva: nueva,
                        confirmar: confirmar
                    })
                });

                const resultado = await respuesta.json();

                if (!respuesta.ok) {
                    alert(resultado.mensaje || "No fue posible cambiar la contraseña.");
                    return;
                }

                document.getElementById("contrasenaActual").value = "";
                document.getElementById("nuevaContrasena").value = "";
                document.getElementById("confirmarContrasena").value = "";

                mostrarNotificacion(
                    "¡Contraseña actualizada!",
                    resultado.mensaje
                );

            } catch (error) {
                console.error("Error al cambiar contraseña:", error);
                alert("No fue posible conectar con el servidor.");

            } finally {
                guardarPerfil.disabled = false;
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

 // ---------- NOTIFICACIONES ----------//
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


/* =========================================
   PUBLICACIONES GENERALES RIUL
========================================= */

let publicacionesEstudiante = [];

async function cargarPublicacionesEstudiante() {
    const lista = document.getElementById("listaPubs");
    const buscador = document.getElementById("buscarPub");

    if (!lista) return;

    lista.innerHTML = '<p class="vacio">Cargando publicaciones...</p>';

    try {
        const respuesta = await fetch("/estudiante/api/publicaciones");

        if (!respuesta.ok) {
            throw new Error("No fue posible consultar las publicaciones.");
        }

        const datos = await respuesta.json();

        publicacionesEstudiante = datos.publicaciones || [];

        const total = document.getElementById("totalPublicaciones");
        const academicas = document.getElementById("totalAcademicas");

        if (total) total.textContent = datos.total || 0;
        if (academicas) academicas.textContent = datos.academicas || 0;

        pintarPublicacionesEstudiante();

    } catch (error) {
        console.error("Error al cargar publicaciones:", error);
        lista.innerHTML =
            '<p class="vacio">No fue posible cargar las publicaciones.</p>';
    }
}

function pintarPublicacionesEstudiante() {
    const lista = document.getElementById("listaPubs");
    const buscador = document.getElementById("buscarPub");

    if (!lista) return;

    const busqueda = (buscador?.value || "").trim().toLowerCase();

    const resultados = publicacionesEstudiante.filter(p => {
        return (
            (p.autor || "").toLowerCase().includes(busqueda) ||
            (p.contenido || "").toLowerCase().includes(busqueda) ||
            (p.semillerо || "").toLowerCase().includes(busqueda)
        );
    });

    if (!resultados.length) {
        lista.innerHTML =
            '<p class="vacio">Todavía no hay publicaciones disponibles.</p>';
        return;
    }

    lista.innerHTML = resultados.map(p => {
        const iniciales = (p.autor || "Usuario")
            .split(" ")
            .slice(0, 2)
            .map(nombre => nombre.charAt(0))
            .join("")
            .toUpperCase();

        const archivo = p.archivo
            ? `<a class="pub-archivo" href="${esc(p.archivo.ruta)}" target="_blank" rel="noopener">
                    ${esc(p.archivo.nombre)}
               </a>`
            : "";

        return `
            <article class="tarjeta pub" data-publicacion="${p.id}">

                <div class="pub-cab">
                    <span class="pub-avatar">${esc(iniciales)}</span>

                    <div class="pub-autor">
                        <b>${esc(p.autor)}</b>
                        <small>${esc(p.rol || "Usuario")} · ${esc(p.fecha)}</small>
                        ${p.semillero
                            ? `<small>Semillero: ${esc(p.semillero)}</small>`
                            : ""}
                    </div>
                </div>

                ${p.academica
                    ? '<span class="pub-etiqueta-academica">Publicación académica</span>'
                    : ""}

                <p class="pub-texto">${esc(p.contenido)}</p>

                ${archivo}

                <div class="pub-stats">
                    <span>${p.reacciones} reacciones · ${p.comentarios} comentarios</span>
                </div>

                <div class="pub-botones">
                    <button
                        type="button"
                        data-accion="like"
                        data-id="${p.id}"
                        class="${p.yo_reaccione ? "activo" : ""}">
                        ${svg("heart")} Me gusta
                    </button>

                    <button
                        type="button"
                        data-accion="comentar"
                        data-id="${p.id}">
                        ${svg("chat")} Comentar
                    </button>
                </div>

                <div class="pub-comentarios" id="comentarios-${p.id}" hidden></div>

            </article>
        `;
    }).join("");
}

function inicializarPublicaciones() {
    const buscador = document.getElementById("buscarPub");
    const lista = document.getElementById("listaPubs");
    const btnPublicar = document.getElementById("btnPublicar");
    const formPub = document.getElementById("formPub");

    if (!lista || lista.dataset.inicializado === "true") return;

    lista.dataset.inicializado = "true";

    cargarPublicacionesEstudiante();

    buscador?.addEventListener("input", pintarPublicacionesEstudiante);

    btnPublicar?.addEventListener("click", () => {
        if (formPub) {
            formPub.hidden = !formPub.hidden;
        }
    });

    formPub?.addEventListener("submit", async evento => {
        evento.preventDefault();

        const texto = document.getElementById("pubTexto");
        const archivo = document.getElementById("pubArchivo");

        if (!texto.value.trim()) return;

        const datos = new FormData();
        datos.append("contenido", texto.value.trim());

        if (archivo.files.length) {
            datos.append("archivo", archivo.files[0]);
        }

        const boton = formPub.querySelector('[type="submit"]');
        boton.disabled = true;
        boton.textContent = "Publicando...";

        try {
            const respuesta = await fetch("/estudiante/api/publicaciones", {
                method: "POST",
                body: datos
            });

            const resultado = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(resultado.mensaje || "No se pudo publicar.");
            }

            formPub.reset();
            formPub.hidden = true;

            await cargarPublicacionesEstudiante();
            mostrarMensajePublicaciones(resultado.mensaje, "exito");

        } catch (error) {
            mostrarMensajePublicaciones(error.message, "error");
        } finally {
            boton.disabled = false;
            boton.textContent = "Publicar contenido";
        }
    });

    lista.addEventListener("click", async evento => {
        const boton = evento.target.closest("[data-accion]");
        if (!boton) return;

        const id = boton.dataset.id;
        const accion = boton.dataset.accion;

        if (accion === "like") {
            boton.disabled = true;

            try {
                const respuesta = await fetch(
                    `/estudiante/api/publicaciones/${id}/reaccion`,
                    { method: "POST" }
                );

                const resultado = await respuesta.json();

                if (!respuesta.ok) {
                    throw new Error(resultado.mensaje);
                }

                await cargarPublicacionesEstudiante();

            } catch (error) {
                mostrarMensajePublicaciones(error.message, "error");
            } finally {
                boton.disabled = false;
            }
        }

        if (accion === "comentar") {
            await cargarComentariosEstudiante(id);
        }
    });
}

async function cargarComentariosEstudiante(id) {
    const contenedor = document.getElementById(`comentarios-${id}`);

    if (!contenedor) return;

    if (!contenedor.hidden) {
        contenedor.hidden = true;
        return;
    }

    contenedor.hidden = false;
    contenedor.innerHTML = '<p>Cargando comentarios...</p>';

    try {
        const respuesta = await fetch(
            `/estudiante/api/publicaciones/${id}/comentarios`
        );

        if (!respuesta.ok) {
            throw new Error("No fue posible cargar los comentarios.");
        }

        const comentarios = await respuesta.json();

        contenedor.innerHTML = `
            <div class="pub-comentarios-lista">
                ${comentarios.length
                    ? comentarios.map(c => `
                        <div class="pub-comentario">
                            <b>${esc(c.autor)}</b>
                            <p>${esc(c.contenido)}</p>
                            <small>${esc(c.fecha)}</small>
                        </div>
                    `).join("")
                    : "<p>Sé el primero en comentar.</p>"
                }
            </div>

            <form class="form-comentario" data-id="${id}">
                <input
                    type="text"
                    name="contenido"
                    maxlength="1000"
                    placeholder="Escribe un comentario..."
                    required
                >
                <button type="submit">Enviar</button>
            </form>
        `;

        contenedor.querySelector("form").addEventListener("submit", async e => {
            e.preventDefault();

            const input = e.target.elements.contenido;
            const contenido = input.value.trim();

            if (!contenido) return;

            try {
                const respuesta = await fetch(
                    `/estudiante/api/publicaciones/${id}/comentarios`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ contenido })
                    }
                );

                const resultado = await respuesta.json();

                if (!respuesta.ok) {
                    throw new Error(resultado.mensaje);
                }

                await cargarComentariosEstudiante(id);
                contenedor.hidden = false;
                await cargarPublicacionesEstudiante();

                mostrarMensajePublicaciones(resultado.mensaje, "exito");

            } catch (error) {
                mostrarMensajePublicaciones(error.message, "error");
            }
        });

    } catch (error) {
        contenedor.innerHTML =
            `<p>${esc(error.message)}</p>`;
    }
}

function mostrarMensajePublicaciones(mensaje, tipo) {
    let elemento = document.getElementById("mensajePublicaciones");

    if (!elemento) {
        elemento = document.createElement("p");
        elemento.id = "mensajePublicaciones";

        const contenido = document.getElementById("contenido-publicaciones");
        contenido?.prepend(elemento);
    }

    if (!elemento) return;

    elemento.className = `mensaje-publicaciones ${tipo}`;
    elemento.textContent = mensaje;
    elemento.hidden = false;
}

// ==============================
// PANEL DE NOTIFICACIONES
// ==============================

const btnNotificaciones = document.getElementById("btnNotificaciones");
const panelNotificaciones = document.getElementById("panelNotificaciones");
const marcarTodasLeidas = document.getElementById("marcarTodasLeidas");
const badgeNotif = document.getElementById("badgeNotif");
const listaNotificaciones = document.getElementById("listaNotificaciones");

const TIPOS_NOTIFICACION = {
    VINCULACION:  { icono: "🌱", titulo: "Semillero" },
    PERFIL:       { icono: "👤", titulo: "Mi perfil" },
    LOGRO:        { icono: "🏆", titulo: "Logro" },
    CONVOCATORIA: { icono: "📢", titulo: "Convocatoria" },
    EVENTO:       { icono: "📅", titulo: "Evento" }
};

function textoHace(minutos) {
    if (minutos < 1) return "Hace un momento";

    if (minutos < 60) {
        return "Hace " + minutos + (minutos === 1 ? " minuto" : " minutos");
    }

    const horas = Math.floor(minutos / 60);

    if (horas < 24) {
        return "Hace " + horas + (horas === 1 ? " hora" : " horas");
    }

    const dias = Math.floor(horas / 24);
    return "Hace " + dias + (dias === 1 ? " día" : " días");
}

function actualizarBadgeNotificaciones(cantidad) {
    if (!badgeNotif) return;

    badgeNotif.textContent = cantidad;
    badgeNotif.hidden = cantidad === 0;
}

async function cargarNotificaciones() {
    if (!listaNotificaciones) return;

    try {
        const respuesta = await fetch("/estudiante/api/notificaciones");

        if (!respuesta.ok) {
            throw new Error("Error " + respuesta.status);
        }

        const datos = await respuesta.json();

        actualizarBadgeNotificaciones(datos.no_leidas);

        if (datos.notificaciones.length === 0) {
            listaNotificaciones.innerHTML =
                '<p class="notificaciones-vacio">No tienes notificaciones.</p>';
            return;
        }

        listaNotificaciones.innerHTML = datos.notificaciones.map(n => {
            const tipo = TIPOS_NOTIFICACION[n.tipo] ||
                { icono: "🔔", titulo: "Notificación" };

            return `
                <div class="notificacion ${n.leida ? "leida" : "no-leida"}">
                    <span class="notif-icono">${tipo.icono}</span>
                    <div>
                        <strong>${tipo.titulo}</strong>
                        <p>${esc(n.mensaje)}</p>
                        <small>${textoHace(n.minutos)}</small>
                    </div>
                </div>`;
        }).join("");

    } catch (error) {
        console.error("Error al cargar notificaciones:", error);
        listaNotificaciones.innerHTML =
            '<p class="notificaciones-vacio">No fue posible cargar las notificaciones.</p>';
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

        if (!panelNotificaciones.hidden) {
            cargarNotificaciones();
        }
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
    marcarTodasLeidas.addEventListener("click", async function() {
        try {
            const respuesta = await fetch(
                "/estudiante/api/notificaciones/leidas",
                { method: "POST" }
            );

            if (!respuesta.ok) {
                throw new Error("Error " + respuesta.status);
            }

            document.querySelectorAll(
                "#listaNotificaciones .notificacion"
            ).forEach(notificacion => {
                notificacion.classList.remove("no-leida");
                notificacion.classList.add("leida");
            });

            actualizarBadgeNotificaciones(0);

        } catch (error) {
            console.error("Error al marcar notificaciones:", error);
        }
    });
}

cargarNotificaciones();


// ---------- MIS PROYECTOS ----------

function cargarMisProyectos() {

    const contenedor = document.getElementById("listaMisProyectos");

    if (!contenedor) return;
 
    fetch("/estudiante/api/proyectos")
    .then(respuesta => {
        if (!respuesta.ok) {
            throw new Error("Error al consultar los proyectos");
        }

        return respuesta.json();
    })
    .then(proyectos => {
            

            document.getElementById("totalProyectos").textContent =
                proyectos.length;

            document.getElementById("proyectosDesarrollo").textContent =
                proyectos.filter(p => p.estado === "EN DESARROLLO").length;

            document.getElementById("proyectosFinalizados").textContent =
                proyectos.filter(p => p.estado === "FINALIZADO").length;

            if (proyectos.length === 0) {
                contenedor.innerHTML =
                    "<p>Tus semilleros todavía no tienen proyectos registrados.</p>";
                return;
            }

            contenedor.innerHTML = proyectos.map(proyecto => `
                <div class="item-proyecto">
                    <h4>${esc(proyecto.titulo)}</h4>
                    <p>${esc(proyecto.descripcion || "Sin descripción")}</p>
                    <p><strong>Semillero:</strong> ${esc(proyecto.semillero)}</p>
                    <p><strong>Fecha de inicio:</strong> ${esc(proyecto.fecha_inicio)}</p>
                    <span class="estado-proyecto">
                        ${esc(proyecto.estado)}
                    </span>
                </div>
            `).join("");

        })
        .catch(error => {
            console.error("Error al cargar proyectos:", error);
            contenedor.innerHTML =
                "<p>Error al consultar tus proyectos.</p>";
        });
}


// VENTANA DE CERRAR SESION
const modalCerrarSesion = document.getElementById("modalCerrarSesion");
const cancelarCerrarSesion = document.getElementById("cancelarCerrarSesion");
const confirmarCerrarSesion = document.getElementById("confirmarCerrarSesion");

const enlaceCerrarSesion = document.querySelector(".cerrar-sesion");
console.log("JS ESTUDIANTE CARGADO");
console.log("ENLACE ENCONTRADO:", enlaceCerrarSesion);
console.log("MODAL ENCONTRADO:", modalCerrarSesion);
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

// MOSTRAR CONTADOR INICIAL
actualizarBadgeNotificaciones();

// MOSTRAR DATOS INICIALES
filtrarRanking(); 
pintarPubs();
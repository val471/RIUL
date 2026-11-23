(function () {
    const fetchOriginal = window.fetch.bind(window);

    window.fetch = async function (...args) {
        const respuesta = await fetchOriginal(...args);

        const aLogin = respuesta.redirected &&
                       respuesta.url.includes('/iniciar-sesion');

        if (aLogin || respuesta.status === 401) {
            window.location.href = '/iniciar-sesion';
        }

        return respuesta;
    };
})();

// TITULOS DE LOS MODULOS
const titles = {
    inicio: 'Inicio',
    usuarios: 'Usuarios',
    facultades: 'Facultades y Programas',
    semilleros: 'Semilleros',
    eventos: 'Convocatorias y Eventos',
    logros: 'Validacion de logros',
    solicitudes: 'Solicitudes',
    reportes: 'reportes',
    ranking: 'Top 10 de clasificacion'
};


 // NAVEGACION ENTRE MODULOS
document.querySelectorAll('.admin-nav a[data-page]').forEach(link => {
    link.addEventListener('click', async event => {
        event.preventDefault();

        const page = link.dataset.page;
        const section = document.getElementById('page-' + page);

        if (!section) {
            console.error('No existe el modulo:', page);
            return;
        }

        // Ocultar los demas modulos
        document.querySelectorAll('.admin-page').forEach(seccion => {
            seccion.classList.remove('active-page');
        });

        // Mostrar el modulo seleccionado
        section.classList.add('active-page');

        // Actualizar menu
        document.querySelectorAll('.admin-nav a').forEach(a => {
            a.classList.toggle('active', a === link);
        });

        // Actualizar titulo
        document.getElementById('topTitle').textContent =
            titles[page] || 'Administracion';

        // CARGAR MODULO DE USUARIOS
        if (page === 'usuarios' && section.dataset.loaded !== 'true') {
            section.innerHTML = '<p>Cargando usuarios...</p>';

            try {
                const response = await fetch('/admin/usuarios');

                if (!response.ok) {
                    throw new Error('Error ' + response.status);
                }

                section.innerHTML = await response.text();
                section.dataset.loaded = 'true';

            } catch (error) {
                console.error('Error al cargar usuarios:', error);
                section.innerHTML =
                    '<p>No se pudieron cargar los usuarios.</p>';
            }
        }

        // CARGAR MODULO DE FACULTADES
        if (page === 'facultades' && section.dataset.loaded !== 'true') {
            section.innerHTML = '<p>Cargando facultades...</p>';

            try {
                const response = await fetch('/admin/facultades');

                if (!response.ok) {
                    throw new Error('Error ' + response.status);
                }

                section.innerHTML = await response.text();
                section.dataset.loaded = 'true';

            } catch (error) {
                console.error('Error al cargar facultades:', error);
                section.innerHTML =
                    '<p>No se pudieron cargar las facultades.</p>';
            }
        } 

        // CARGAR MODULO DE SEMILLEROS
        if (page === 'semilleros' && section.dataset.loaded !== 'true') {
            section.innerHTML = '<p>Cargando semilleros...</p>';

            try {
                const response = await fetch('/admin/semilleros');

                if (!response.ok) {
                    throw new Error('Error ' + response.status);
                }

                section.innerHTML = await response.text();
                section.dataset.loaded = 'true';

            } catch (error) {
                console.error('Error al cargar semilleros:', error);
                section.innerHTML =
                    '<p>No se pudieron cargar los semilleros.</p>';
            }
        }

        // CARGAR MODULO DE CONVOCATORIAS
        if (page === 'eventos' && section.dataset.loaded !== 'true') {
            section.innerHTML = '<p>Cargando convocatorias...</p>';

            try {
                const response = await fetch('/admin/convocatorias');

                if (!response.ok) {
                    throw new Error('Error ' + response.status);
                }

                section.innerHTML = await response.text();
                section.dataset.loaded = 'true';

            } catch (error) {
                console.error('Error al cargar convocatorias:', error);
                section.innerHTML =
                    '<p>No se pudieron cargar las convocatorias.</p>';
            }
        }

        // CARGAR SOLICITUDES
        // Se recargan cada vez que se abre el modulo
        if (page === 'solicitudes') {
            await cargarSolicitudes(section);
        }
    }); 
}); 


// BOTONES "VER SOLICITUDES" DEL INICIO
document.querySelectorAll('.admin-page a[data-page]').forEach(enlace => {
    enlace.addEventListener('click', event => {
        event.preventDefault();

        const menu = document.querySelector(
            '.admin-nav a[data-page="' + enlace.dataset.page + '"]'
        );

        if (menu) {
            menu.click();
        }
    });
});

// SOLICITUDES DE REGISTRO
async function cargarSolicitudes(section) {
    section = section || document.getElementById('page-solicitudes');

    section.innerHTML = '<p>Cargando solicitudes...</p>';

    try {
        const response = await fetch('/admin/solicitudes');

        if (!response.ok) {
            throw new Error('Error ' + response.status);
        }

        section.innerHTML = await response.text();
         
        // Conectar los botones del modal despues de cargar el HTML
        configurarModalRechazo();


    } catch (error) {
        console.error(error);
        section.innerHTML = '<p>No se pudieron cargar las solicitudes.</p>';
    }
}

function mostrarAvisoSolicitud(texto, tipo) {
    const aviso = document.getElementById('avisoSolicitudes');

    if (!aviso) {
        return;
    }

    aviso.textContent = texto;
    aviso.className = 'aviso-solicitudes ' + tipo;
    aviso.hidden = false;
}
let solicitudPendienteRechazo = null;
let cambioPendienteRechazo = null;


async function resolverSolicitud(boton, accion) {
    const item = boton.closest('.request-item');
    const id = boton.dataset.id;

    if (accion === 'rechazar') {
        solicitudPendienteRechazo = {
            id: id,
            item: item
        };

        document.getElementById('motivoRechazo').value = '';
        document.getElementById('errorMotivoRechazo').hidden = true;
        document.getElementById('modalRechazoCambio').hidden = false;

        return;
    }

    const confirmado = await confirmarAccion({
        titulo: 'Aprobar registro',
        mensaje: 'Se creará la cuenta del usuario y quedará activa. ¿Deseas aprobar la solicitud?',
        aceptar: 'Sí, aprobar'
    });

    if (!confirmado) return;

    procesarSolicitudRegistro(item, id, accion);
} 

async function procesarSolicitudRegistro(item, id, accion, motivo = '') {
    item.querySelectorAll('button').forEach(b => b.disabled = true);

    try {
        const response = await fetch(
            '/admin/api/solicitudes/' + id + '/' + accion,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ motivo: motivo })
            }
        );

        const resultado = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                resultado.mensaje || 'No fue posible completar la acción.'
            );
        }

        await cargarSolicitudes();

        mostrarAvisoSolicitud(resultado.mensaje, 'exito');

        return true;

    } catch (error) {
        item.querySelectorAll('button').forEach(b => b.disabled = false);

        mostrarAvisoSolicitud(error.message, 'error');

        return false;
    }
}
// Mostrat solicitudes de cambio de datos 
function mostrarTipoSolicitud(tipo, boton) {

    document.getElementById("panel-registro").hidden = tipo !== "registro";
    document.getElementById("panel-cambios").hidden = tipo !== "cambios";

    document.querySelectorAll(".tab-solicitud").forEach(tab => {
        tab.classList.remove("activa");
    });

    boton.classList.add("activa");

    if (tipo === "cambios") {
        cargarSolicitudesCambios();
    }
}

async function cargarSolicitudesCambios() {

    const contenedor = document.getElementById("requestsCambios");

    try {
        const respuesta = await fetch("/admin/solicitudes/actualizaciones");
        const solicitudes = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error("No se pudieron cargar las solicitudes.");
        }

        if (solicitudes.length === 0) {
            contenedor.innerHTML = "<p>No hay solicitudes pendientes.</p>";
            return;
        }

        contenedor.innerHTML = solicitudes.map(solicitud => `
    <article class="request-item">

        <div class="request-info">
            <strong>${solicitud.nombre}</strong>
            <small>${solicitud.correo}</small>
            <small>Dato solicitado: ${solicitud.campo}</small>
            <small>Valor anterior: ${solicitud.valor_anterior || "No registrado"}</small>
            <small>Nuevo valor: ${solicitud.valor_nuevo}</small>
            <small>Motivo: ${solicitud.descripcion || "Sin descripción"}</small>
            <small>Fecha: ${solicitud.fecha}</small>
        </div>

        <span class="status pendiente">PENDIENTE</span>

        <div class="request-actions">
            <button onclick="aprobarCambio(${solicitud.id})">
                Aprobar
            </button>
            <button onclick="rechazarCambio(${solicitud.id})">
                Rechazar
            </button>
        </div>

    </article>
     `).join("");

    } catch (error) {
        console.error(error);
        contenedor.innerHTML = "<p>Error al cargar las solicitudes.</p>";
    }
}


// BOTONES DEL MODAL DE RECHAZO


 // BOTONES DEL MODAL DE RECHAZO

function configurarModalRechazo() {

    const modalRechazo = document.getElementById('modalRechazoCambio');

    if (!modalRechazo) return;

    const motivoRechazo = modalRechazo.querySelector('#motivoRechazo');
    const errorMotivo = modalRechazo.querySelector('#errorMotivoRechazo');
    const botonConfirmarRechazo = modalRechazo.querySelector('#confirmarRechazo');
    const btnCerrarRechazo = modalRechazo.querySelector('#cerrarModalRechazo');
    const btnCancelarRechazo = modalRechazo.querySelector('#cancelarRechazo');

    function cerrarModalRechazo() {
        modalRechazo.hidden = true;
        motivoRechazo.value = '';
        errorMotivo.hidden = true;

        solicitudPendienteRechazo = null;
        cambioPendienteRechazo = null;
    }

    btnCerrarRechazo.onclick = cerrarModalRechazo;
    btnCancelarRechazo.onclick = cerrarModalRechazo;

    botonConfirmarRechazo.onclick = async () => {

        const motivo = motivoRechazo.value.trim();

        if (!motivo) {
            errorMotivo.textContent = 'Debes escribir el motivo del rechazo.';
            errorMotivo.hidden = false;
            return;
        }

        botonConfirmarRechazo.disabled = true;

        try {

            // RECHAZAR SOLICITUD DE REGISTRO
            if (solicitudPendienteRechazo) {

                const solicitud = solicitudPendienteRechazo;

                const exito = await procesarSolicitudRegistro(
                    solicitud.item,
                    solicitud.id,
                    'rechazar',
                    motivo
                );

                if (!exito) return;

                cerrarModalRechazo();
                return;
            }

            // RECHAZAR CAMBIO DE DATOS
            if (cambioPendienteRechazo) {

                const respuesta = await fetch(
                    `/admin/solicitudes/actualizaciones/${cambioPendienteRechazo.id}/rechazar`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ motivo: motivo })
                    }
                );

                const resultado = await respuesta.json();

                if (!respuesta.ok) {
                    throw new Error(resultado.mensaje);
                }

                cerrarModalRechazo();
                await cargarSolicitudesCambios();
            }

        } catch (error) {

            errorMotivo.textContent =
                error.message || 'No se pudo rechazar la solicitud.';

            errorMotivo.hidden = false;

        } finally {
            botonConfirmarRechazo.disabled = false;
        }
    };
}


// FILTRAR USUARIOS
function filterUsers() {
    const q = document.getElementById('searchUsers').value.toLowerCase();
    const role = document.getElementById('filterRole').value;

    document.querySelectorAll('#usersTable tr[data-rol]').forEach(row => {
        row.hidden = !(
            row.textContent.toLowerCase().includes(q) &&
            (!role || row.dataset.rol === role)
        );
    });
}

// ACTIVAR O SUSPENDER USUARIOS (guarda en MySQL)
async function toggleUser(button) {
    const row = button.closest('tr');
    const nuevoEstado = button.dataset.nuevo;
    const nombre = row.querySelector('strong').textContent;
    const verbo = nuevoEstado === 'ACTIVO' ? 'activar' : 'suspender';
    const confirmado = await confirmarAccion({
    titulo: nuevoEstado === 'ACTIVO' ? 'Activar cuenta' : 'Suspender cuenta',
    mensaje: '¿Seguro que quieres ' + verbo + ' la cuenta de ' + nombre + '?',
    aceptar: nuevoEstado === 'ACTIVO' ? 'Sí, activar' : 'Sí, suspender'
    });

    if (!confirmado) return;

    button.disabled = true;

    try {
        const respuesta = await fetch('/admin/api/usuarios/' + row.dataset.id + '/estado', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ estado: nuevoEstado })
        });
        const datos = await respuesta.json().catch(() => ({}));

        if (!respuesta.ok) {
            alert(datos.mensaje || 'No fue posible cambiar el estado.');
            button.disabled = false;
            return;
        }

        const activo = nuevoEstado === 'ACTIVO';
        const estado = row.querySelector('.status');
        estado.classList.toggle('suspended', !activo);
        estado.textContent = activo ? 'Activo' : 'Suspendido';

        button.textContent = activo ? 'Suspender' : 'Activar';
        button.dataset.nuevo = activo ? 'SUSPENDIDO' : 'ACTIVO';
        button.className = activo ? 'btn btn-soft-red' : 'btn';
    } catch (error) {
        console.error(error);
        alert('No fue posible conectar con el servidor.');
    }

    button.disabled = false;
}

// GENERAR reporte
function generateReport() {
    const output = document.getElementById('reportOutput');

    output.textContent =
        'reporte demostrativo RIUL\n' +
        'Usuarios mostrados: ' +
        document.querySelectorAll('#usersTable tr').length +
        '\nFecha: ' +
        new Date().toLocaleDateString('es-CO') +
        '\n\nLos datos no provienen de la base de datos.';

    output.hidden = false;
}

// ==============================
// FACULTADES Y PROGRAMAS
// ==============================

// Filtra las tarjetas por nombre de facultad o de programa
function filterFacultades() {
    const q = document.getElementById('searchFacultades').value.toLowerCase();
    let visibles = 0;

    document.querySelectorAll('#listaFacultades .facultad-card').forEach(card => {
        const mostrar = card.textContent.toLowerCase().includes(q);
        card.hidden = !mostrar;
        if (mostrar) visibles++;
    });

    document.getElementById('sinFacultades').hidden = visibles > 0;
}

function abrirModalFac(id) {
    document.getElementById(id).hidden = false;
}

function cerrarModalFac(id) {
    document.getElementById(id).hidden = true;
}

// Vuelve a pedir el módulo al servidor para ver lo recién guardado
async function recargarFacultades() {
    const seccion = document.getElementById('page-facultades');
    const respuesta = await fetch('/admin/facultades');
    if (respuesta.ok) {
        seccion.innerHTML = await respuesta.text();
    }
}

async function enviarJsonFac(url, metodo, cuerpo) {
    const respuesta = await fetch(url, {
        method: metodo,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(cuerpo)
    });
    const datos = await respuesta.json().catch(() => ({}));
    return { ok: respuesta.ok, datos: datos };
}

// ---------- CREAR / EDITAR FACULTAD ----------
function crearFacultad() {
    const modal = document.getElementById('modalFacultad');
    const input = document.getElementById('inputNombreFacultad');

    modal.dataset.id = '';
    document.getElementById('tituloModalFacultad').textContent = 'Nueva facultad';
    document.getElementById('errorModalFacultad').hidden = true;
    input.value = '';

    abrirModalFac('modalFacultad');
    input.focus();
}

function editarFacultad(boton) {
    const card = boton.closest('.facultad-card');
    const modal = document.getElementById('modalFacultad');
    const input = document.getElementById('inputNombreFacultad');

    modal.dataset.id = card.dataset.id;
    document.getElementById('tituloModalFacultad').textContent = 'Editar facultad';
    document.getElementById('errorModalFacultad').hidden = true;
    input.value = card.querySelector('h3').textContent.trim();

    abrirModalFac('modalFacultad');
    input.focus();
}

async function guardarFacultad() {
    const modal = document.getElementById('modalFacultad');
    const nombre = document.getElementById('inputNombreFacultad').value.trim();
    const error = document.getElementById('errorModalFacultad');
    const boton = document.getElementById('btnGuardarFacultad');
    const id = modal.dataset.id;

    if (!nombre) {
        error.textContent = 'Escribe el nombre de la facultad.';
        error.hidden = false;
        return;
    }

    boton.disabled = true;

    try {
        const resultado = await enviarJsonFac(
            id ? '/admin/api/facultades/' + id : '/admin/api/facultades',
            id ? 'PUT' : 'POST',
            { nombre: nombre }
        );

        if (!resultado.ok) {
            error.textContent = resultado.datos.mensaje || 'No fue posible guardar.';
            error.hidden = false;
            boton.disabled = false;
            return;
        }

        cerrarModalFac('modalFacultad');
        await recargarFacultades();
    } catch (e) {
        console.error(e);
        error.textContent = 'No fue posible conectar con el servidor.';
        error.hidden = false;
        boton.disabled = false;
    }
}

// ---------- CREAR PROGRAMA ----------
function crearPrograma(boton) {
    const card = boton.closest('.facultad-card');
    const modal = document.getElementById('modalPrograma');
    const input = document.getElementById('inputNombrePrograma');

    modal.dataset.facultad = card.dataset.id;
    document.getElementById('subtituloModalPrograma').textContent =
        'Se agregará a: ' + card.querySelector('h3').textContent.trim();
    document.getElementById('errorModalPrograma').hidden = true;
    input.value = '';

    abrirModalFac('modalPrograma');
    input.focus();
}

async function guardarPrograma() {
    const modal = document.getElementById('modalPrograma');
    const nombre = document.getElementById('inputNombrePrograma').value.trim();
    const error = document.getElementById('errorModalPrograma');
    const boton = document.getElementById('btnGuardarPrograma');

    if (!nombre) {
        error.textContent = 'Escribe el nombre del programa.';
        error.hidden = false;
        return;
    }

    boton.disabled = true;

    try {
        const resultado = await enviarJsonFac(
            '/admin/api/facultades/' + modal.dataset.facultad + '/programas',
            'POST',
            { nombre: nombre }
        );

        if (!resultado.ok) {
            error.textContent = resultado.datos.mensaje || 'No fue posible guardar.';
            error.hidden = false;
            boton.disabled = false;
            return;
        }

        cerrarModalFac('modalPrograma');
        await recargarFacultades();
    } catch (e) {
        console.error(e);
        error.textContent = 'No fue posible conectar con el servidor.';
        error.hidden = false;
        boton.disabled = false;
    }
}

// ---------- USUARIOS MATRICULADOS ----------
async function verUsuariosFacultad(boton) {
    const card = boton.closest('.facultad-card');
    const cuerpo = document.getElementById('tablaUsuariosFac');
    const resumen = document.getElementById('resumenUsuariosFac');
    const ROLES = {
        ESTUDIANTE: 'Estudiante investigador',
        DOCENTE_LIDER: 'Docente líder'
    };

    document.getElementById('tituloUsuariosFac').textContent =
        'Usuarios matriculados · ' + card.querySelector('h3').textContent.trim();
    document.getElementById('buscarUsuariosFac').value = '';
    resumen.textContent = '';
    cuerpo.innerHTML = '<tr><td colspan="4">Cargando...</td></tr>';
    abrirModalFac('modalUsuariosFac');

    try {
        const respuesta = await fetch('/admin/api/facultades/' + card.dataset.id + '/usuarios');
        const datos = await respuesta.json();

        if (!respuesta.ok) throw new Error(datos.mensaje || 'Error');

        cuerpo.innerHTML = '';

        if (!datos.usuarios.length) {
            cuerpo.innerHTML = '<tr><td colspan="4">Esta facultad aún no tiene usuarios matriculados.</td></tr>';
            return;
        }

        datos.usuarios.forEach(u => {
            const fila = document.createElement('tr');

            const tdUsuario = document.createElement('td');
            const nombre = document.createElement('strong');
            nombre.textContent = u.nombre;
            const correo = document.createElement('small');
            correo.textContent = u.correo;
            correo.style.display = 'block';
            tdUsuario.append(nombre, correo);

            const tdPrograma = document.createElement('td');
            tdPrograma.textContent = u.detalle || '—';

            const tdRol = document.createElement('td');
            tdRol.textContent = ROLES[u.rol] || u.rol;

            const tdEstado = document.createElement('td');
            const estado = document.createElement('span');
            const activo = u.estado === 'ACTIVO';
            estado.className = 'status' + (activo ? '' : ' suspended');
            estado.textContent = activo ? 'Activo' : 'Suspendido';
            tdEstado.appendChild(estado);

            fila.append(tdUsuario, tdPrograma, tdRol, tdEstado);
            cuerpo.appendChild(fila);
        });

        resumen.textContent = datos.usuarios.length +
            (datos.usuarios.length === 1 ? ' usuario' : ' usuarios');
    } catch (e) {
        console.error(e);
        cuerpo.innerHTML = '<tr><td colspan="4">No fue posible cargar los usuarios.</td></tr>';
    }
}

function filtrarUsuariosFac() {
    const q = document.getElementById('buscarUsuariosFac').value.toLowerCase();
    document.querySelectorAll('#tablaUsuariosFac tr').forEach(fila => {
        fila.hidden = !fila.textContent.toLowerCase().includes(q);
    });
}


// MOSTRAR U OCULTAR PROGRAMAS Y SEMILLEROS
function mostrarLista(boton) {
    const grupo = boton.closest('.facultad-grupo');
    const lista = grupo.querySelector('.lista-elementos');

    lista.hidden = !lista.hidden;

    if (lista.hidden) {
        boton.textContent = grupo.querySelector('strong').textContent === 'Programas'
            ? 'Ver programas'
            : 'Ver semilleros';
    } else {
        boton.textContent = 'Ocultar lista';
    }
}
// BUSCAR SEMILLEROS
function filtrarSemilleros() {
    const buscador = document.getElementById('buscarSemilleros');

    if (!buscador) return;

    const texto = buscador.value.toLowerCase().trim();
    const tarjetas = document.querySelectorAll(
        '#listaSemilleros .semillero-card'
    );

    tarjetas.forEach(tarjeta => {
        tarjeta.hidden = !tarjeta.textContent.toLowerCase().includes(texto);
    });
}

// ==============================
// SEMILLEROS (ADMIN)
// ==============================
async function recargarSemilleros() {
    const seccion = document.getElementById('page-semilleros');
    const respuesta = await fetch('/admin/semilleros');
    if (respuesta.ok) {
        seccion.innerHTML = await respuesta.text();
    }
}

function limpiarErrorSemillero() {
    document.getElementById('errorModalSemillero').hidden = true;
}


// ASIGNAR DOCENTE LIDER
async function abrirAsignacionDocente(id) {
    const modal = document.getElementById('modalAsignarDocente');
    const select = document.getElementById('selectDocenteLider');
    const error = document.getElementById('errorAsignarDocente');

    document.getElementById('idSemilleroAsignacion').value = id;

    select.innerHTML = '<option value="">Sin docente líder</option>';
    error.hidden = true;
    error.textContent = '';

    modal.hidden = false;

    try {
        const respuesta = await fetch(
            '/admin/api/semilleros/' + id + '/docentes-disponibles'
        );

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.mensaje || 'No fue posible cargar los docentes.');
        }

        datos.docentes.forEach(docente => {
            const opcion = document.createElement('option');
            opcion.value = docente.id_usuario;
            opcion.textContent = docente.nombre_institucional;

            if (Number(docente.id_semillero_liderado) === Number(id)) {
                opcion.selected = true;
            }

            select.appendChild(opcion);
        });

    } catch (e) {
        console.error('Error al cargar docentes:', e);
        error.textContent = e.message;
        error.hidden = false;
    }
}

async function guardarAsignacionDocente() {
    const id = document.getElementById('idSemilleroAsignacion').value;
    const select = document.getElementById('selectDocenteLider');
    const error = document.getElementById('errorAsignarDocente');
    const boton = document.getElementById('btnGuardarAsignacion');

    error.hidden = true;
    boton.disabled = true;

    try {
        const respuesta = await fetch(
            '/admin/api/semilleros/' + id + '/docente-lider',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id_usuario: select.value || null
                })
            }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.mensaje || 'No fue posible guardar la asignación.');
        }

        cerrarModalFac('modalAsignarDocente');
        await recargarSemilleros();

    } catch (e) {
        console.error('Error al asignar docente:', e);
        error.textContent = e.message;
        error.hidden = false;
    } finally {
        boton.disabled = false;
    }
}


// ---------- CREAR ----------
function crearSemillero() {
    const modal = document.getElementById('modalSemillero');

    modal.dataset.id = '';
    document.getElementById('tituloModalSemillero').textContent = 'Nuevo semillero';
    document.getElementById('semNombre').value = '';
    document.getElementById('semFacultad').value = '';
    document.getElementById('semLinea').value = '';
    document.getElementById('semCupo').value = '20';
    document.getElementById('semDescripcion').value = '';
    limpiarErrorSemillero();

    abrirModalFac('modalSemillero');
    document.getElementById('semNombre').focus();
}

// ---------- EDITAR ----------
async function editarSemillero(id) {
    try {
        const respuesta = await fetch('/admin/api/semilleros/' + id);
        const datos = await respuesta.json();

        if (!respuesta.ok) {
            alert(datos.mensaje || 'No fue posible cargar el semillero.');
            return;
        }

        const s = datos.semillero;
        const modal = document.getElementById('modalSemillero');

        modal.dataset.id = id;
        document.getElementById('tituloModalSemillero').textContent = 'Editar semillero';
        document.getElementById('semNombre').value = s.nombre || '';
        document.getElementById('semFacultad').value = s.id_facultad;
        document.getElementById('semLinea').value = s.linea_investigacion || '';
        document.getElementById('semCupo').value = s.cupo_maximo;
        document.getElementById('semDescripcion').value = s.descripcion || '';
        limpiarErrorSemillero();

        abrirModalFac('modalSemillero');
        document.getElementById('semNombre').focus();
    } catch (e) {
        console.error(e);
        alert('No fue posible conectar con el servidor.');
    }
}

async function guardarSemillero() {
    const modal = document.getElementById('modalSemillero');
    const error = document.getElementById('errorModalSemillero');
    const boton = document.getElementById('btnGuardarSemillero');
    const id = modal.dataset.id;

    const cuerpo = {
        nombre: document.getElementById('semNombre').value.trim(),
        id_facultad: document.getElementById('semFacultad').value,
        linea_investigacion: document.getElementById('semLinea').value.trim(),
        cupo_maximo: document.getElementById('semCupo').value,
        descripcion: document.getElementById('semDescripcion').value.trim()
    };

    if (!cuerpo.nombre) {
        error.textContent = 'Escribe el nombre del semillero.';
        error.hidden = false;
        return;
    }
    if (!cuerpo.id_facultad) {
        error.textContent = 'Selecciona la facultad.';
        error.hidden = false;
        return;
    }

    boton.disabled = true;

    try {
        const resultado = await enviarJsonFac(
            id ? '/admin/api/semilleros/' + id : '/admin/api/semilleros',
            id ? 'PUT' : 'POST',
            cuerpo
        );

        if (!resultado.ok) {
            error.textContent = resultado.datos.mensaje || 'No fue posible guardar.';
            error.hidden = false;
            boton.disabled = false;
            return;
        }

        cerrarModalFac('modalSemillero');
        await recargarSemilleros();
    } catch (e) {
        console.error(e);
        error.textContent = 'No fue posible conectar con el servidor.';
        error.hidden = false;
        boton.disabled = false;
    }
}

// ---------- DAR DE BAJA / REACTIVAR ----------
async function cambiarEstadoSemillero(boton) {
    const card = boton.closest('.semillero-card');
    const nombre = card.querySelector('h3').textContent.trim();
    const nuevo = boton.dataset.nuevo;
    const verbo = nuevo === 'ACTIVO' ? 'reactivar' : 'dar de baja';
    const confirmado = await confirmarAccion({
    titulo: nuevo === 'ACTIVO' ? 'Reactivar semillero' : 'Dar de baja semillero',
    mensaje: '¿Seguro que quieres ' + verbo + ' el semillero "' + nombre + '"?',
    aceptar: 'Sí, continuar'
    });

    if (!confirmado) return;

    boton.disabled = true;

    try {
        const resultado = await enviarJsonFac(
            '/admin/api/semilleros/' + card.dataset.id + '/estado',
            'POST',
            { estado: nuevo }
        );

        if (!resultado.ok) {
            alert(resultado.datos.mensaje || 'No fue posible cambiar el estado.');
            boton.disabled = false;
            return;
        }

        await recargarSemilleros();
    } catch (e) {
        console.error(e);
        alert('No fue posible conectar con el servidor.');
        boton.disabled = false;
    }
}

// ---------- DETALLE ----------
function agregarDatoSem(contenedor, etiqueta, valor, ancho) {
    const caja = document.createElement('div');
    caja.className = 'det-sem-dato' + (ancho ? ' ancho' : '');

    const titulo = document.createElement('small');
    titulo.textContent = etiqueta;

    const contenido = document.createElement('strong');
    contenido.textContent = valor || '—';

    caja.append(titulo, contenido);
    contenedor.appendChild(caja);
}

async function verDetalleSemillero(id) {
    const nombre = document.getElementById('detSemNombre');
    const subtitulo = document.getElementById('detSemSubtitulo');
    const datosCaja = document.getElementById('detSemDatos');
    const integrantes = document.getElementById('detSemIntegrantes');
    const proyectos = document.getElementById('detSemProyectos');

    nombre.textContent = 'Cargando...';
    subtitulo.textContent = '';
    datosCaja.innerHTML = '';
    integrantes.innerHTML = '';
    proyectos.innerHTML = '';
    abrirModalFac('modalDetalleSemillero');

    try {
        const respuesta = await fetch('/admin/api/semilleros/' + id);
        const datos = await respuesta.json();

        if (!respuesta.ok) throw new Error(datos.mensaje || 'Error');

        const s = datos.semillero;

        nombre.textContent = s.nombre;
        subtitulo.textContent = s.facultad + ' · ' +
            (s.estado === 'ACTIVO' ? 'Activo' : 'Inactivo');

        agregarDatoSem(datosCaja, 'Docente líder', s.docente_lider);
        agregarDatoSem(datosCaja, 'Línea de investigación', s.linea_investigacion);
        agregarDatoSem(datosCaja, 'Cupo',
            datos.integrantes.length + ' de ' + s.cupo_maximo + ' integrantes');
        agregarDatoSem(datosCaja, 'XP acumulado', String(s.xp_total));
        agregarDatoSem(datosCaja, 'Descripción', s.descripcion, true);

        if (!datos.integrantes.length) {
            integrantes.innerHTML = '<tr><td colspan="3">Aún no tiene integrantes.</td></tr>';
        }

        datos.integrantes.forEach(i => {
            const fila = document.createElement('tr');
            [i.nombre, i.programa || '—', i.ingreso || '—'].forEach(texto => {
                const celda = document.createElement('td');
                celda.textContent = texto;
                fila.appendChild(celda);
            });
            integrantes.appendChild(fila);
        });

        if (!datos.proyectos.length) {
            const vacio = document.createElement('li');
            vacio.textContent = 'Aún no tiene proyectos.';
            proyectos.appendChild(vacio);
        }

        datos.proyectos.forEach(p => {
            const item = document.createElement('li');
            item.textContent = p.titulo + ' (' + p.estado + ')';
            proyectos.appendChild(item);
        });
    } catch (e) {
        console.error(e);
        nombre.textContent = 'No fue posible cargar el semillero.';
    }
}

// VER DETALLES DE CONVOCATORIA
function verDetalleConvocatoria(boton) {
    const id = boton.dataset.id;
    console.log('Ver convocatoria:', id);
}

// CONVOCATORIAS: CREAR, EDITAR Y ELIMINAR (RF-02)
const modalConvocatoria = document.getElementById('modalConvocatoria');
const formConvocatoria = document.getElementById('formConvocatoria');
const mensajeConvocatoria = document.getElementById('mensajeConvocatoria');
const tituloModalConvocatoria = document.getElementById('tituloModalConvocatoria');

// null = se está creando; con un número = se está editando esa convocatoria
let convocatoriaEditando = null;

function abrirFormularioConvocatoria() {
    formConvocatoria.reset();
    mensajeConvocatoria.textContent = '';
    modalConvocatoria.hidden = false;
}
function crearConvocatoria() {
    convocatoriaEditando = null;
    tituloModalConvocatoria.textContent = 'Nueva convocatoria';
    abrirFormularioConvocatoria();
}

async function editarConvocatoria(boton) {
    try {
        const respuesta = await fetch('/admin/api/convocatorias/' + boton.dataset.id);
        const c = await respuesta.json();

        if (!respuesta.ok) {
            alert(c.mensaje || 'No fue posible cargar la convocatoria.');
            return;
        }

        convocatoriaEditando = boton.dataset.id;
        tituloModalConvocatoria.textContent = 'Editar convocatoria';
        abrirFormularioConvocatoria();

        document.getElementById('convTitulo').value = c.titulo;
        document.getElementById('convDescripcion').value = c.descripcion;
        document.getElementById('convInicio').value = c.fecha_inicio;
        document.getElementById('convCierre').value = c.fecha_cierre;
        document.getElementById('convModalidad').value = c.modalidad;

    } catch (error) {
        alert('No fue posible cargar la convocatoria.');
    }
}

async function eliminarConvocatoria(boton) {
   const confirmado = await confirmarAccion({
    titulo: 'Eliminar convocatoria',
    mensaje: 'Esta acción no se puede deshacer. ¿Deseas eliminarla?',
    aceptar: 'Sí, eliminar'
    });

    if (!confirmado) return;
    try {
        const respuesta = await fetch(
            '/admin/api/convocatorias/' + boton.dataset.id,
            { method: 'DELETE' }
        );
        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            alert(resultado.mensaje || 'No fue posible eliminar la convocatoria.');
            return;
        }

        await recargarConvocatorias();

    } catch (error) {
        alert('No fue posible eliminar la convocatoria.');
    }
}

async function recargarConvocatorias() {
    const section = document.getElementById('page-eventos');
    const response = await fetch('/admin/convocatorias');

    if (response.ok) {
        section.innerHTML = await response.text();
    }
}

document.getElementById('cancelarConvocatoria')?.addEventListener('click', function () {
    modalConvocatoria.hidden = true;
});

formConvocatoria?.addEventListener('submit', async function (e) {
 mensajeConvocatoria.textContent = 'Guardando...';

    const datos = {
        titulo: document.getElementById('convTitulo').value,
        descripcion: document.getElementById('convDescripcion').value,
        fecha_inicio: document.getElementById('convInicio').value,
        fecha_cierre: document.getElementById('convCierre').value,
        modalidad: document.getElementById('convModalidad').value
    };

    const editando = convocatoriaEditando !== null;
    const url = editando
        ? '/admin/api/convocatorias/' + convocatoriaEditando
        : '/admin/api/convocatorias';

    try {
        const respuesta = await fetch(url, {
            method: editando ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });
        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            mensajeConvocatoria.textContent =
                resultado.mensaje || 'No fue posible guardar la convocatoria.';
            return;
        }

        modalConvocatoria.hidden = true;
        await recargarConvocatorias();

    } catch (error) {
        mensajeConvocatoria.textContent = 'No fue posible guardar la convocatoria.';
    }

});

// ==============================
// VENTANA DE CONFIRMACIÓN Y AVISOS
// ==============================
// Uso: const ok = await confirmarAccion({ titulo, mensaje, aceptar });
function confirmarAccion(opciones) {
    const o = Object.assign({
        titulo: '¿Estás seguro?',
        mensaje: '',
        aceptar: 'Aceptar',
        cancelar: 'Cancelar'
    }, opciones || {});

    return new Promise(function (resolver) {
        const fondo = document.createElement('div');
        fondo.className = 'confirmar-fondo';

        const caja = document.createElement('div');
        caja.className = 'confirmar-caja';
        caja.setAttribute('role', 'dialog');
        caja.setAttribute('aria-modal', 'true');

        const titulo = document.createElement('h2');
        titulo.textContent = o.titulo;

        const mensaje = document.createElement('p');
        mensaje.textContent = o.mensaje;

        const botones = document.createElement('div');
        botones.className = 'confirmar-botones';

        const btnCancelar = document.createElement('button');
        btnCancelar.type = 'button';
        btnCancelar.className = 'btn';
        btnCancelar.textContent = o.cancelar;

        const btnAceptar = document.createElement('button');
        btnAceptar.type = 'button';
        btnAceptar.className = 'btn btn-red';
        btnAceptar.textContent = o.aceptar;

        function cerrar(resultado) {
            document.removeEventListener('keydown', alTeclear);
            fondo.remove();
            resolver(resultado);
        }

        function alTeclear(e) {
            if (e.key === 'Escape') cerrar(false);
        }

        btnCancelar.addEventListener('click', function () { cerrar(false); });
        btnAceptar.addEventListener('click', function () { cerrar(true); });
        fondo.addEventListener('click', function (e) {
            if (e.target === fondo) cerrar(false);
        });
        document.addEventListener('keydown', alTeclear);

        botones.append(btnCancelar, btnAceptar);
        caja.append(titulo, mensaje, botones);
        fondo.appendChild(caja);
        document.body.appendChild(fondo);

        btnAceptar.focus();
    });
}

// Aviso corto que desaparece solo (reemplaza al alert)
function mostrarToast(mensaje, tipo) {
    const aviso = document.createElement('div');
    aviso.className = 'toast-admin ' + (tipo || '');
    aviso.textContent = mensaje;
    document.body.appendChild(aviso);
    setTimeout(function () { aviso.remove(); }, 3500);
}

async function aprobarCambio(id) {

    const confirmado = await confirmarAccion({
        titulo: 'Aprobar solicitud',
        mensaje: 'Se aplicará el cambio solicitado a los datos del usuario. ¿Deseas aprobarla?',
        aceptar: 'Sí, aprobar'
    });

    if (!confirmado) return;

    try {
        const respuesta = await fetch(
            `/admin/solicitudes/actualizaciones/${id}/aprobar`,
            { method: "POST" }
        );

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(resultado.mensaje);
        }

        mostrarToast(resultado.mensaje, 'exito');
        cargarSolicitudesCambios();

    } catch (error) {
        console.error(error);
        mostrarToast(error.message || "No se pudo aprobar la solicitud.", 'error');
    }
}

function rechazarCambio(id) {

    cambioPendienteRechazo = {
        id: id
    };

    document.getElementById('motivoRechazo').value = '';
    document.getElementById('errorMotivoRechazo').hidden = true;
    document.getElementById('modalRechazoCambio').hidden = false;
}


// ==============================
// NOTIFICACIONES DEL ADMINISTRADOR
// ==============================
(function () {
    const btn = document.getElementById('btnNotifAdmin');
    const panel = document.getElementById('panelNotifAdmin');
    const lista = document.getElementById('listaNotifAdmin');
    const badge = document.getElementById('badgeNotifAdmin');
    const resumen = document.getElementById('resumenNotifAdmin');
    let ultimoTotal = null;
    if (!btn || !panel || !lista) return;

    const TIPOS = {
        REGISTRO:      { icono: '👤', titulo: 'Registro' },
        ACTUALIZACION: { icono: '✏️', titulo: 'Actualización de datos' },
        LIDERAZGO:     { icono: '🎓', titulo: 'Liderazgo de semillero' },
        LOGRO:         { icono: '🏆', titulo: 'Logro por validar' }
    };

    function escapar(texto) {
        const d = document.createElement('div');
        d.textContent = texto == null ? '' : String(texto);
        return d.innerHTML;
    }

    function haceCuanto(min) {
        if (min < 1) return 'Hace un momento';
        if (min < 60) return 'Hace ' + min + ' min';
        const h = Math.floor(min / 60);
        if (h < 24) return 'Hace ' + h + (h === 1 ? ' hora' : ' horas');
        const d = Math.floor(h / 24);
        return 'Hace ' + d + (d === 1 ? ' día' : ' días');
    }

    function pintarBadge(total) {
        badge.textContent = total > 9 ? '9+' : total;
        badge.hidden = total === 0;
        resumen.textContent = total === 0 ? '' : total + ' pendiente' + (total === 1 ? '' : 's');
    }

     
    async function cargar() {
        try {
            const r = await fetch('/admin/api/notificaciones');
            if (!r.ok) throw new Error('Error ' + r.status);
            const datos = await r.json();

            pintarBadge(datos.total);

            const seccion = document.getElementById('page-solicitudes');

         if (ultimoTotal !== null && datos.total !== ultimoTotal &&
         seccion && seccion.classList.contains('active-page') &&
         typeof cargarSolicitudes === 'function') {
         cargarSolicitudes(seccion);
          }

          ultimoTotal = datos.total;

            if (!datos.notificaciones.length) {
                lista.innerHTML = '<p class="admin-notif-vacio">No tienes notificaciones pendientes.</p>';
                return;
            }

            lista.innerHTML = datos.notificaciones.map(n => {
                const t = TIPOS[n.tipo] || { icono: '🔔', titulo: 'Notificación', 
                                           logro:{ icono: '🏆', titulo: 'Logro por validar' },
                                           RESUELTA:      { icono: '✅', titulo: 'Solicitud resuelta' } };
                return '<button type="button" class="admin-notif-item" data-destino="' + escapar(n.destino) + '">' +
                    '<span class="admin-notif-icono">' + t.icono + '</span>' +
                    '<span><strong>' + t.titulo + '</strong>' +
                    '<p>' + escapar(n.mensaje) + '</p>' +
                    '<small>' + haceCuanto(n.minutos) + '</small></span>' +
                    '</button>';
            }).join('');
        } catch (e) {
            console.error('Error al cargar notificaciones:', e);
            lista.innerHTML = '<p class="admin-notif-vacio">No fue posible cargar las notificaciones.</p>';
        }
    }

    function cerrar() {
        panel.hidden = true;
        btn.setAttribute('aria-expanded', 'false');
    }

    btn.addEventListener('click', function (e) {
        e.stopPropagation();
        panel.hidden = !panel.hidden;
        btn.setAttribute('aria-expanded', String(!panel.hidden));
        if (!panel.hidden) cargar();
    });

    // Clic en una notificación: ir al módulo correspondiente
    lista.addEventListener('click', function (e) {
        const item = e.target.closest('.admin-notif-item');
        if (!item) return;
        const enlace = document.querySelector('.admin-nav a[data-page="' + item.dataset.destino + '"]');
        if (enlace) enlace.click();
        cerrar();
    });

    document.addEventListener('click', function (e) {
        if (!panel.contains(e.target) && !btn.contains(e.target)) cerrar();
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') cerrar();
    });

    // Contador inicial y refresco cada 60 s
    cargar();
    setInterval(cargar, 15000);
})();

// VENTANA CERRAR SESION
const modalCerrarSesion = document.getElementById('modalCerrarSesion');
const enlaceCerrarSesion = document.querySelector('.admin-logout');

enlaceCerrarSesion?.addEventListener('click', function (e) {
    e.preventDefault();
    modalCerrarSesion.hidden = false;
});

document.getElementById('cancelarCerrarSesion')?.addEventListener('click', function () {
    modalCerrarSesion.hidden = true;
});

document.getElementById('confirmarCerrarSesion')?.addEventListener('click', function () {
    window.location.href = '/cerrar-sesion';
});






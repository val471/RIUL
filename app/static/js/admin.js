// TITULOS DE LOS MODULOS
const titles = {
    inicio: 'Inicio',
    usuarios: 'Usuarios',
    facultades: 'Facultades y Programas',
    semilleros: 'Semilleros',
    eventos: 'Convocatorias y Eventos',
    logros: 'Validacion de logros',
    solicitudes: 'Solicitudes',
    informes: 'Informes',
    ranking: 'Top 10 de clasificacion'
};


// NAVEGACION ENTRE MODULOS
document.querySelectorAll('.admin-nav a[data-page]').forEach(link => {
    link.addEventListener('click', async event => {
        event.preventDefault();

        const page = link.dataset.page;
        const section = document.getElementById('page-' + page);

        document.querySelectorAll('.admin-page').forEach(section => {
            section.classList.remove('active-page');
        });

        section.classList.add('active-page');

        document.querySelectorAll('.admin-nav a').forEach(a => {
            a.classList.toggle('active', a === link);
        });

        document.getElementById('topTitle').textContent = titles[page];
          
        // Modudo facultad
        if (page === 'facultades' && section.dataset.loaded !== 'true') {
            section.innerHTML = '<p>Cargando facultades...</p>';

            try {
                const response = await fetch('/admin/facultades');

                if (!response.ok) {
                    throw new Error('Error al cargar facultades');
                }

                section.innerHTML = await response.text();
                section.dataset.loaded = 'true';

            } catch (error) {
                console.error(error);
                section.innerHTML = '<p>No se pudieron cargar las facultades.</p>';
            }
        }


        // CARGAR MODULO DE SEMILLEROS
        if (page === 'semilleros' && section.dataset.loaded !== 'true') {
        section.innerHTML = '<p>Cargando semilleros...</p>';

        try {
        const response = await fetch('/admin/semilleros');

        if (!response.ok) {
            throw new Error('Error al cargar semilleros');
        }

        section.innerHTML = await response.text();
        section.dataset.loaded = 'true';

        } catch (error) {
        console.error(error);
        section.innerHTML = '<p>No se pudieron cargar los semilleros.</p>';
        }
        }

        // CARGAR MODULO DE CONVOCATORIAS
        if (page === 'eventos' && section.dataset.loaded !== 'true') {
        section.innerHTML = '<p>Cargando convocatorias...</p>';

        try {
        const response = await fetch('/admin/convocatorias');

        if (!response.ok) {
            throw new Error('Error al cargar convocatorias');
        }

        section.innerHTML = await response.text();
        section.dataset.loaded = 'true';

        } catch (error) {
        console.error(error);
        section.innerHTML = '<p>No se pudieron cargar las convocatorias.</p>';
       }
       }
       
        // CARGAR MODULO DE SOLICITUDES (se recarga cada vez que se abre)
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

async function resolverSolicitud(boton, accion) {
    const item = boton.closest('.request-item');
    const id = boton.dataset.id;

    if (accion === 'rechazar' &&
        !confirm('¿Deseas rechazar esta solicitud? La cuenta no será creada.')) {
        return;
    }

    item.querySelectorAll('button').forEach(b => b.disabled = true);

    try {
        const response = await fetch(
            '/admin/api/solicitudes/' + id + '/' + accion,
            { method: 'POST' }
        );

        const resultado = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(
                resultado.mensaje || 'No fue posible completar la acción.'
            );
        }

        await cargarSolicitudes();
        mostrarAvisoSolicitud(resultado.mensaje, 'exito');

    } catch (error) {
        item.querySelectorAll('button').forEach(b => b.disabled = false);
        mostrarAvisoSolicitud(error.message, 'error');
    }
}

// FILTRAR USUARIOS
function filterUsers() {
    const q = document.getElementById('searchUsers').value.toLowerCase();
    const role = document.getElementById('filterRole').value;

    document.querySelectorAll('#usersTable tr').forEach(row => {
        row.hidden = !(
            row.textContent.toLowerCase().includes(q) &&
            (!role || row.cells[2].querySelector('select').value === role)
        );
    });
}

// ACTIVAR O SUSPENDER USUARIOS
function toggleUser(button) {
    const row = button.closest('tr');
    const status = row.querySelector('.status');

    const suspended = status.classList.toggle('suspended');

    status.textContent = suspended ? 'Suspendido' : 'Activo';
    button.textContent = suspended ? 'Activar' : 'Suspender';
}

// AGREGAR ELEMENTOS
function addItem(id, label) {
    const name = prompt(label + ':');

    if (!name || !name.trim()) {
        return;
    }

    const p = document.createElement('p');
    p.textContent = name.trim();

    document.getElementById(id).appendChild(p);
}

// GENERAR INFORME
function generateReport() {
    const output = document.getElementById('reportOutput');

    output.textContent =
        'Informe demostrativo RIUL\n' +
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

// Filtra las tarjetas por nombre de facultad
function filterFacultades() {
    const q = document.getElementById('searchFacultades').value.toLowerCase();
    let visibles = 0;

    document.querySelectorAll('#listaFacultades .facultad-card').forEach(card => {
        const nombre = card.querySelector('h3').textContent.toLowerCase();
        const mostrar = nombre.includes(q);

        card.hidden = !mostrar;
        if (mostrar) visibles++;
    });

    document.getElementById('sinFacultades').hidden = visibles > 0;
}

// Crea una tarjeta nueva
function crearFacultad() {
    const nombre = prompt('Nombre de la facultad:');
    if (!nombre || !nombre.trim()) return;

    const card = document.createElement('article');
    card.className = 'facultad-card';
    card.innerHTML =
        '<div class="facultad-top">' +
            '<div class="facultad-icon"><svg viewBox="0 0 24 24"><rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 21v-4h6v4"/></svg></div>' +
            '<button class="link-editar" onclick="editarFacultad(this)">Editar</button>' +
        '</div>' +
        '<h3></h3>' +
        '<p class="facultad-meta">0 programas · 0 semilleros</p>' +
        '<button class="btn" onclick="vincularSemillero(this)">Vincular semillero</button>';

    // textContent evita que el nombre escrito se interprete como HTML
    card.querySelector('h3').textContent = nombre.trim();
    document.getElementById('listaFacultades').appendChild(card);
}

// Cambia el nombre de una facultad
function editarFacultad(boton) {
    const titulo = boton.closest('.facultad-card').querySelector('h3');
    const nuevo = prompt('Nuevo nombre de la facultad:', titulo.textContent);

    if (!nuevo || !nuevo.trim()) return;
    titulo.textContent = nuevo.trim();
}

// Suma un semillero al contador de la facultad
function vincularSemillero(boton) {
    const card = boton.closest('.facultad-card');
    const facultad = card.querySelector('h3').textContent;
    const semillero = prompt('Nombre del semillero a vincular a ' + facultad + ':');

    if (!semillero || !semillero.trim()) return;

    const meta = card.querySelector('.facultad-meta');
    meta.textContent = meta.textContent.replace(
        /(\d+) semilleros/,
        (texto, n) => (Number(n) + 1) + ' semilleros'
    );

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
    if (!confirm('¿Deseas eliminar esta convocatoria?')) {
        return;
    }

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

document.getElementById('cancelarConvocatoria').addEventListener('click', function () {
    modalConvocatoria.hidden = true;
});

formConvocatoria.addEventListener('submit', async function (e) {
    e.preventDefault();
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






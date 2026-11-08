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
    link.addEventListener('click', event => {
        event.preventDefault();

        const page = link.dataset.page;

        document.querySelectorAll('.admin-page').forEach(section => {
            section.classList.remove('active-page');
        });

        document.getElementById('page-' + page).classList.add('active-page');

        document.querySelectorAll('.admin-nav a').forEach(a => {
            a.classList.toggle('active', a === link);
        });

        document.getElementById('topTitle').textContent = titles[page];
    });
});

// RESOLVER SOLICITUDES
function resolveRequest(button, state) {
    const item = button.closest('.request-item');
    const estado = item.querySelector('.status');

    estado.textContent = state;
    estado.className = 'status' + (state === 'Rechazada' ? ' suspended' : '');

    item.querySelector('.request-actions').remove();
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
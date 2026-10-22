
document.addEventListener("DOMContentLoaded", function () {
    // Normaliza textos para que las búsquedas no dependan
    // de las mayúsculas ni de los acentos.
    function normalizar(texto) {
        return (texto || "")
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    // Filtros de semilleros
    const buscarSemillero = document.getElementById("buscarSemillero");
    const areaSemillero = document.getElementById("areaSemillero");
    const listaSemilleros = document.getElementById("listaSemilleros");
    const sinSemilleros = document.getElementById("sinSemilleros");

    function filtrarSemilleros() {
        if (!listaSemilleros) return;

        const texto = normalizar(buscarSemillero?.value);
        const area = areaSemillero?.value || "";
        let visibles = 0;

        listaSemilleros.querySelectorAll(".tarjeta").forEach(function (tarjeta) {
            const coincideTexto = normalizar(tarjeta.dataset.nombre)
                .includes(texto);
            const coincideArea = !area || tarjeta.dataset.area === area;
            const mostrar = coincideTexto && coincideArea;

            tarjeta.hidden = !mostrar;
            if (mostrar) visibles++;
        });

        if (sinSemilleros) sinSemilleros.hidden = visibles > 0;
    }

    buscarSemillero?.addEventListener("input", filtrarSemilleros);
    areaSemillero?.addEventListener("change", filtrarSemilleros);

    // Filtros de proyectos
    const buscarProyecto = document.getElementById("buscarProyecto");
    const estadoProyecto = document.getElementById("estadoProyecto");
    const listaProyectos = document.getElementById("listaProyectos");
    const sinProyectos = document.getElementById("sinProyectos");

    function filtrarProyectos() {
        if (!listaProyectos) return;

        const texto = normalizar(buscarProyecto?.value);
        const estado = estadoProyecto?.value || "";
        let visibles = 0;

        listaProyectos.querySelectorAll(".tarjeta").forEach(function (tarjeta) {
            const coincideTexto = normalizar(tarjeta.dataset.nombre)
                .includes(texto);
            const coincideEstado = !estado || tarjeta.dataset.estado === estado;
            const mostrar = coincideTexto && coincideEstado;

            tarjeta.hidden = !mostrar;
            if (mostrar) visibles++;
        });

        if (sinProyectos) sinProyectos.hidden = visibles > 0;
    }

    buscarProyecto?.addEventListener("input", filtrarProyectos);
    estadoProyecto?.addEventListener("change", filtrarProyectos);

    // Muestra los detalles de un proyecto
    window.mostrarDetalleProyecto = function (boton) {
        const detalle = document.getElementById("detalleProyecto");
        if (!detalle) return;

        detalle.textContent = boton.dataset.detalle || "No hay detalles disponibles.";
        detalle.hidden = false;
        detalle.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };

    // Filtros de eventos
    const buscarEvento = document.getElementById("buscarEvento");
    const tipoEvento = document.getElementById("tipoEvento");
    const listaEventos = document.getElementById("listaEventos");
    const sinEventos = document.getElementById("sinEventos");

    function filtrarEventos() {
        if (!listaEventos) return;

        const texto = normalizar(buscarEvento?.value);
        const tipo = tipoEvento?.value || "";
        let visibles = 0;

        listaEventos.querySelectorAll(".tarjeta").forEach(function (tarjeta) {
            const coincideTexto = normalizar(tarjeta.dataset.nombre)
                .includes(texto);
            const coincideTipo = !tipo || tarjeta.dataset.tipo === tipo;
            const mostrar = coincideTexto && coincideTipo;

            tarjeta.hidden = !mostrar;
            if (mostrar) visibles++;
        });

        if (sinEventos) sinEventos.hidden = visibles > 0;
    }

    buscarEvento?.addEventListener("input", filtrarEventos);
    tipoEvento?.addEventListener("change", filtrarEventos);

    // Mensajes para los botones de inscripción de demostración
    window.mostrarAvisoEvento = function (mensaje) {
        const resultado = document.getElementById("mensajeEvento");

        if (resultado) {
            resultado.textContent = mensaje;
        } else {
            alert(mensaje);
        }
    };

    // Formulario de contacto: por ahora valida y muestra un aviso.
    // Todavía no envía ni guarda información en el servidor.
    const formContacto = document.getElementById("formContacto");
    const resultadoContacto = document.getElementById("resultadoContacto");

    formContacto?.addEventListener("submit", function (evento) {
        evento.preventDefault();

        if (!formContacto.reportValidity()) return;

        if (resultadoContacto) {
            resultadoContacto.textContent =
                "El formulario está validado. El envío real se habilitará al conectarlo con Flask.";
        }
    });
});

// Cierra la sesión tras 10 minutos sin actividad (RNF-01)
(function () {
    const LIMITE = 10 * 60 * 1000; // 10 minutos
    let temporizador;

    function reiniciar() {
        clearTimeout(temporizador);
        temporizador = setTimeout(function () {
            window.location.href = "/cerrar-sesion";
        }, LIMITE);
    }

    ["mousemove", "mousedown", "keydown", "scroll", "touchstart", "click"]
        .forEach(function (evento) {
            document.addEventListener(evento, reiniciar, { passive: true });
        });

    reiniciar();
})();
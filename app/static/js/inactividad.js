// Cierra la sesiOn tras N minutos sin actividad (RNF-01).
// La actividad se comparte entre pestañas del mismo navegador, para que
// una pestaña abierta pero quieta no cierre la sesión de otra que sí se usa.
(function () {
    const script = document.currentScript;
    const minutos = parseInt(script && script.dataset.minutos, 10) || 10;
    const LIMITE = minutos * 60 * 1000;
    const CLAVE = "riul_ultima_actividad";

    let ultimaLocal = Date.now();
    let ultimaEscritura = 0;
    let temporizador;

    function leerCompartida() {
        try { return parseInt(localStorage.getItem(CLAVE), 10) || 0; }
        catch (e) { return 0; }
    }

    function actividad() {
        const ahora = Date.now();
        ultimaLocal = ahora;
        // Se escribe como máximo cada 5 segundos
        if (ahora - ultimaEscritura > 5000) {
            ultimaEscritura = ahora;
            try { localStorage.setItem(CLAVE, String(ahora)); } catch (e) {}
        }
    }

    function revisar() {
        const ultima = Math.max(ultimaLocal, leerCompartida());
        const falta = LIMITE - (Date.now() - ultima);

        if (falta <= 0) {
            window.location.href = "/cerrar-sesion";
        } else {
            temporizador = setTimeout(revisar, falta + 500);
        }
    }

    ["mousemove", "mousedown", "keydown", "scroll", "touchstart", "click"]
        .forEach(function (evento) {
            document.addEventListener(evento, actividad, { passive: true });
        });

    actividad();
    temporizador = setTimeout(revisar, LIMITE);
})();
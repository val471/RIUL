

from flask import render_template


def mostrar_panel():
    return render_template("docente/index.html")


def mostrar_semillero():
    return render_template("docente/semillero.html")


def mostrar_integrantes():
    return render_template("docente/integrantes.html")


def mostrar_solicitudes_vinculacion():
    return render_template("docente/solicitudes_vinculacion.html")


def mostrar_proyectos():
    return render_template("docente/proyectos.html")


def mostrar_convocatorias():
    return render_template("docente/convocatorias.html")


def mostrar_eventos():
    return render_template("docente/eventos.html")


def mostrar_publicaciones():
    return render_template("docente/publicaciones.html")


def mostrar_ranking():
    return render_template("docente/ranking.html")


def mostrar_logros():
    return render_template("docente/logros.html")


def mostrar_perfil():
    return render_template("docente/perfil.html")

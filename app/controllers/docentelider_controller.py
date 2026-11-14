
from flask import render_template


def mostrar_panel():
    return render_template("docente_lider/index.html")


def mostrar_semillero():
    return render_template("docente_lider/semilleros.html")


def mostrar_usuarios():
    return render_template("docente_lider/usuario.html")


def mostrar_solicitudes():
    return render_template("docente_lider/solicitudes.html")


def mostrar_proyectos():
    return render_template("docente_lider/proyectos.html")


def mostrar_convocatorias():
    return render_template("docente_lider/convocatorias.html")


def mostrar_eventos():
    return render_template("docente_lider/eventos.html")


def mostrar_publicaciones():
    return render_template("docente_lider/publicaciones.html")


def mostrar_ranking():
    return render_template("docente_lider/ranking.html")


def mostrar_logros():
    return render_template("docente_lider/logros.html")


def mostrar_perfil():
    return render_template("docente_lider/perfil.html")

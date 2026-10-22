
from flask import render_template


def mostrar_panel():
    return render_template("admin/index.html")


def mostrar_usuarios():
    return render_template("admin/usuarios.html")


def mostrar_facultades():
    return render_template("admin/facultades.html")


def mostrar_semilleros():
    return render_template("admin/semilleros.html")


def mostrar_convocatorias():
    return render_template("admin/convocatorias.html")


def mostrar_publicaciones():
    return render_template("admin/publicaciones.html")


def mostrar_logros():
    return render_template("admin/logros.html")


def mostrar_ranking():
    return render_template("admin/ranking.html")


def mostrar_reportes():
    return render_template("admin/reportes.html")


def mostrar_solicitudes():
    return render_template("admin/solicitudes.html")

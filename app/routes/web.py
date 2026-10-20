

from flask import Blueprint, render_template

web = Blueprint("web", __name__)


# PÁGINAS PÚBLICAS
@web.route("/")
def inicio():
    return render_template("index.html")


@web.route("/semilleros")
def semilleros():
    return render_template("visitante/semilleros.html")


@web.route("/proyectos")
def proyectos():
    return render_template("visitante/proyectos.html")


@web.route("/eventos")
def eventos():
    return render_template("visitante/eventos.html")


@web.route("/contacto")
def contacto():
    return render_template("visitante/contacto.html")


# AUTENTICACIÓN
@web.route("/iniciar-sesion")
def iniciar_sesion():
    return render_template("auth/login.html")


@web.route("/registro")
def registro():
    return render_template("auth/registro.html")


# PANELES POR ROL
@web.route("/estudiante")
def panel_estudiante():
    return render_template("estudiante/index.html")


@web.route("/docente")
def panel_docente():
    return render_template("docente/index.html")


@web.route("/administrador")
def panel_administrador():
    return render_template("administrador/index.html")

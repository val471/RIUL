
from flask import Blueprint, render_template

web = Blueprint("web", __name__)


# Páginas públicas
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


# Autenticación: por ahora solo muestra los formularios
@web.route("/iniciar-sesion")
def iniciar_sesion():
    return render_template("auth/login.html")


@web.route("/registro")
def registro():
    return render_template("auth/registro.html")

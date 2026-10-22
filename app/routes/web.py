

from flask import Blueprint, render_template

from app.controllers import visitante_controller
from app.controllers import admin_controller
from app.controllers import estudiante_controller
from app.controllers import docente_controller

web = Blueprint("web", __name__)


# PÁGINAS PÚBLICAS
@web.route("/")
def inicio():
    return visitante_controller.inicio()


@web.route("/semilleros")
def semilleros():
    return visitante_controller.semilleros()


@web.route("/proyectos")
def proyectos():
    return visitante_controller.proyectos()


@web.route("/eventos")
def eventos():
    return visitante_controller.eventos()


@web.route("/contacto")
def contacto():
    return visitante_controller.contacto()


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
    return estudiante_controller.mostrar_panel()


@web.route("/docente")
def panel_docente():
    return docente_controller.mostrar_panel()


@web.route("/admin")
def panel_administrador():
    return admin_controller.mostrar_panel()

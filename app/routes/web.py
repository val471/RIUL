

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


@web.route("/docente/semillero")
def docente_semillero():
    return render_template("docente/semillero.html")


@web.route("/docente/proyectos")
def docente_proyectos():
    return render_template("docente/proyectos.html")


@web.route("/docente/integrantes")
def docente_integrantes():
    return render_template("docente/integrantes.html")


@web.route("/docente/solicitudes-vinculacion")
def docente_solicitudes_vinculacion():
    return render_template("docente/solicitudes_vinculacion.html")


@web.route("/docente/eventos")
def docente_eventos():
    return render_template("docente/eventos.html")


@web.route("/docente/convocatorias")
def docente_convocatorias():
    return render_template("docente/convocatorias.html")


@web.route("/docente/logros")
def docente_logros():
    return render_template("docente/logros.html")


@web.route("/docente/perfil")
def docente_perfil():
    return render_template("docente/perfil.html")


@web.route("/admin")
def panel_administrador():
    return admin_controller.mostrar_panel()

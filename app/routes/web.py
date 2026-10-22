

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


# PANEL ESTUDIANTE
@web.route("/estudiante")
def panel_estudiante():
    return estudiante_controller.mostrar_panel()

# PANEL DOCENTE
@web.route("/docente")
def panel_docente():
    return docente_controller.mostrar_panel()


@web.route("/docente/semillero")
def docente_semillero():
    return docente_controller.mostrar_semillero()


@web.route("/docente/proyectos")
def docente_proyectos():
    return docente_controller.mostrar_proyectos()


@web.route("/docente/integrantes")
def docente_integrantes():
    return docente_controller.mostrar_integrantes()


@web.route("/docente/solicitudes-vinculacion")
def docente_solicitudes_vinculacion():
    return docente_controller.mostrar_solicitudes_vinculacion()


@web.route("/docente/eventos")
def docente_eventos():
    return docente_controller.mostrar_eventos()


@web.route("/docente/convocatorias")
def docente_convocatorias():
    return docente_controller.mostrar_convocatorias()


@web.route("/docente/logros")
def docente_logros():
    return docente_controller.mostrar_logros()


@web.route("/docente/publicaciones")
def docente_publicaciones():
    return docente_controller.mostrar_publicaciones()


@web.route("/docente/ranking")
def docente_ranking():
    return docente_controller.mostrar_ranking()


@web.route("/docente/perfil")
def docente_perfil():
    return docente_controller.mostrar_perfil()


# PANEL DE ADMINISTRADOR
@web.route("/admin")
def panel_administrador():
    return admin_controller.mostrar_panel()


@web.route("/admin/usuarios")
def admin_usuarios():
    return admin_controller.mostrar_usuarios()


@web.route("/admin/facultades")
def admin_facultades():
    return admin_controller.mostrar_facultades()


@web.route("/admin/semilleros")
def admin_semilleros():
    return admin_controller.mostrar_semilleros()


@web.route("/admin/convocatorias")
def admin_convocatorias():
    return admin_controller.mostrar_convocatorias()


@web.route("/admin/publicaciones")
def admin_publicaciones():
    return admin_controller.mostrar_publicaciones()


@web.route("/admin/logros")
def admin_logros():
    return admin_controller.mostrar_logros()


@web.route("/admin/ranking")
def admin_ranking():
    return admin_controller.mostrar_ranking()


@web.route("/admin/reportes")
def admin_reportes():
    return admin_controller.mostrar_reportes()


@web.route("/admin/solicitudes")
def admin_solicitudes():
    return admin_controller.mostrar_solicitudes()

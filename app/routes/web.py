
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
    return render_template(
        "visitante/pagina.html",
        titulo="Contacto",
        descripcion="Comunícate con la Red de Investigación Universidad Libre.",
        seccion="contacto"
    )


# AUTENTICACIÓN VISUAL (sin validaciones de momento para los usuarios)

@web.route("/iniciar-sesion")
def iniciar_sesion():
    return render_template("auth/login.html")


@web.route("/registro")
def registro():
    return render_template("auth/registro.html")


# PÁGINAS DE LOS ROLES (Temporales para navegación)

@web.route("/estudiante")
def estudiante():
    return render_template(
        "visitante/pagina.html",
        titulo="Panel del estudiante",
        descripcion="Aquí podrás consultar tus proyectos, semilleros y actividades de investigación.",
        seccion="estudiante"
    )


@web.route("/docente")
def docente():
    return render_template(
        "visitante/pagina.html",
        titulo="Panel del docente",
        descripcion="Aquí podrás gestionar semilleros, proyectos y actividades de investigación.",
        seccion="docente"
    )


@web.route("/administrador")
def administrador():
    return render_template(
        "visitante/pagina.html",
        titulo="Panel del administrador",
        descripcion="Aquí podrás administrar usuarios y gestionar la plataforma RIUL.",
        seccion="administrador"
    )
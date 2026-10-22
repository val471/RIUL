
from flask import render_template


def inicio():
    return render_template("index.html")


def semilleros():
    return render_template("visitante/semilleros.html")


def proyectos():
    return render_template("visitante/proyectos.html")


def eventos():
    return render_template("visitante/eventos.html")


def contacto():
    return render_template("visitante/contacto.html")

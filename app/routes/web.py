from flask import Blueprint, render_template
from flask import session, redirect, url_for
from flask import request, jsonify
from sqlalchemy import text
from werkzeug.security import check_password_hash
from datetime import datetime
from werkzeug.security import generate_password_hash



from app.controllers import visitante_controller
from app.controllers import admin_controller
from app.controllers import estudiante_controller
from app.controllers import docente_controller
from app.models.usuario import Usuario
from app.models.solicitud_registro import SolicitudRegistro
from app.extensions import db


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
    facultades = db.session.execute(text("""
        SELECT id_facultad, nombre
        FROM facultad
        ORDER BY nombre
    """)).mappings().all()

    programas = db.session.execute(text("""
        SELECT id_programa, nombre, id_facultad
        FROM programa
        ORDER BY nombre
    """)).mappings().all()

    return render_template(
        "auth/registro.html",
        facultades=facultades,
        programas=programas
    )



@web.route("/cerrar-sesion")
def cerrar_sesion():
    session.clear()
    return redirect(url_for("web.inicio"))


# PANEL ESTUDIANTE
@web.route("/estudiante")
def panel_estudiante():
    return estudiante_controller.mostrar_panel()

@web.route("/estudiante/perfil")
def estudiante_perfil():
    return render_template("estudiante/perfil.html")


# SEMILLEROS 

@web.route("/estudiante/semilleros")
def explorar_semilleros():
    return render_template("estudiante/semilleros.html")


# EVENTOS 

@web.route("/estudiante/eventos")
def estudiante_eventos():
    return render_template("estudiante/eventos.html")

# LOGROS
@web.route("/estudiante/logros")
def estudiante_logros():
    return render_template("estudiante/logros.html")

#CONVOCATORIAS

@web.route("/estudiante/convocatorias")
def estudiante_convocatorias():
    return render_template("estudiante/convocatorias.html")

#PUBLICACIONES
@web.route("/estudiante/publicaciones")
def estudiante_publicaciones():
    return render_template("estudiante/publicaciones.html")

#RANKIG
@web.route("/estudiante/rankingestu")
def estudiante_rankingestu():
    return render_template("estudiante/rankingestu.html")

#NOTIFICACIONES
@web.route("/estudiante/notificaciones")
def estudiante_notificaciones():
    return render_template("estudiante/notificaciones.html")

#HOJA_DE VIDA
@web.route("/estudiante/hoja-vida")
def estudiante_hoja_vida():
    return render_template("estudiante/hoja_vida.html")



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


DESTINOS = {"ADMIN": "/admin", "ESTUDIANTE": "/estudiante", "DOCENTE": "/docente"}


@web.route("/api/login", methods=["POST"])
def api_login():
    datos = request.get_json(silent=True) or {}
    correo = (datos.get("correo") or "").strip().lower()
    clave = datos.get("contrasena") or ""

    usuario = Usuario.query.filter_by(correo_institucional=correo).first()

    if (not usuario or usuario.estado != "ACTIVO"
            or not check_password_hash(usuario.contrasena_hash, clave)):
        return jsonify({"mensaje": "Correo o contraseña incorrectos."}), 401

    session["id_usuario"] = usuario.id_usuario
    session["rol"] = usuario.rol
    return jsonify({
        "mensaje": "Acceso correcto.",
        "redirect": DESTINOS.get(usuario.rol, "/"),
    })

@web.route("/api/semilleros")
def api_semilleros():
    filas = db.session.execute(text("""
        SELECT s.id_semillero, s.nombre, s.linea_investigacion, s.estado,
               f.nombre AS facultad
        FROM semillero s
        JOIN facultad f ON f.id_facultad = s.id_facultad
        WHERE s.estado = 'ACTIVO'
        ORDER BY s.nombre
    """)).mappings().all()
    return jsonify([{
        "id": f["id_semillero"],
        "nombre": f["nombre"],
        "linea": f["linea_investigacion"],
        "facultad": f["facultad"],
        "estado": f["estado"],
    } for f in filas])


@web.route("/api/registro", methods=["POST"])
def api_registro():
    datos = request.get_json(silent=True) or {}

    nombres = (datos.get("nombres") or "").strip()
    apellidos = (datos.get("apellidos") or "").strip()
    correo = (datos.get("correo") or "").strip().lower()
    documento = (datos.get("documento") or "").strip()
    fecha_nacimiento = datos.get("fecha_nacimiento")
    rol = datos.get("rol")
    id_facultad = datos.get("id_facultad")
    id_programa = datos.get("id_programa")
    contrasena = datos.get("contrasena") or ""

    if not all([nombres, apellidos, correo, documento,
                fecha_nacimiento, rol, id_facultad, contrasena]):
        return jsonify({"mensaje": "Completa todos los campos obligatorios."}), 400

    if not correo.endswith("@unilibre.edu.co"):
        return jsonify({"mensaje": "Debes utilizar tu correo institucional."}), 400

    if rol not in ["ESTUDIANTE", "DOCENTE"]:
        return jsonify({"mensaje": "El rol seleccionado no es válido."}), 400

    if rol == "ESTUDIANTE" and not id_programa:
        return jsonify({"mensaje": "Selecciona tu programa académico."}), 400

    if Usuario.query.filter_by(correo_institucional=correo).first():
        return jsonify({"mensaje": "Este correo ya está registrado."}), 409

    if SolicitudRegistro.query.filter_by(
        correo_institucional=correo,
        estado="PENDIENTE"
    ).first():
        return jsonify({"mensaje": "Ya existe una solicitud pendiente con este correo."}), 409

    try:
        fecha = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()

        solicitud = SolicitudRegistro(
            nombre_completo=f"{nombres} {apellidos}",
            correo_institucional=correo,
            fecha_nacimiento=fecha,
            documento=documento,
            id_facultad=int(id_facultad),
            id_programa=int(id_programa) if rol == "ESTUDIANTE" else None,
            contrasena_hash=generate_password_hash(contrasena),
            rol_solicitado=rol,
            estado="PENDIENTE",
            fecha_solicitud=datetime.now()
        )

        db.session.add(solicitud)
        db.session.commit()

        return jsonify({
            "mensaje": "Tu solicitud fue enviada y está pendiente de aprobación."
        }), 201

    except ValueError as error:
        db.session.rollback()
        print("ERROR DE VALIDACION:", repr(error))
        return jsonify({
            "mensaje": "La fecha o los datos seleccionados no son válidos."
        }), 400

    except Exception as error:
        db.session.rollback()
        print("ERROR AL GUARDAR SOLICITUD:", repr(error))
        return jsonify({
            "mensaje": "No fue posible guardar la solicitud."
        }), 500

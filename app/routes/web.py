import os
import re
import time
from flask import Blueprint, render_template
from flask import session, redirect, url_for
from flask import request, jsonify
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash





from app.controllers import visitante_controller
from app.controllers import admin_controller
from app.controllers import estudiante_controller
from app.controllers import docentelider_controller
from app.models.usuario import Usuario
from app.models.solicitud_registro import SolicitudRegistro
from app.extensions import db
from datetime import datetime
from app.models.solicitud_actualizacion import SolicitudActualizacion


web = Blueprint("web", __name__)
EXTENSIONES_FOTO = {"png", "jpg", "jpeg", "webp"}
PESO_MAX_FOTO = 2 * 1024 * 1024  # 2 MB


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
@web.route("/estudiante/logros-estudiante")
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

def _usuario_actual():
    return db.session.get(Usuario, session.get("id_usuario"))



# PANEL DOCENTE


# PANEL DOCENTE
@web.before_request
def proteger_panel_docente():
    """Solo un usuario con rol DOCENTE puede entrar a /docentelider/..."""
    if request.path.startswith("/docentelider") and session.get("rol") != "DOCENTE":
        if request.path.startswith("/docentelider/api"):
            return jsonify({"mensaje": "No autorizado"}), 401
        return redirect(url_for("web.iniciar_sesion"))
    
@web.route("/docentelider")
def panel_docente():
    return docentelider_controller.mostrar_panel()


@web.route("/docentelider/semilleros")
def docente_semillero():
    return docentelider_controller.mostrar_semillero()


@web.route("/docentelider/proyectos")
def docente_proyectos():
    return docentelider_controller.mostrar_proyectos()


@web.route("/docentelider/usuario")
def docente_usuarios():
    return docentelider_controller.mostrar_usuarios()


@web.route("/docentelider/solicitudes")
def docente_solicitudes():
    return docentelider_controller.mostrar_solicitudes()


@web.route("/docentelider/eventos")
def docente_eventos():
    return docentelider_controller.mostrar_eventos()


@web.route("/docentelider/convocatorias")
def docente_convocatorias():
    return docentelider_controller.mostrar_convocatorias()


@web.route("/docentelider/logros")
def docente_logros():
    return docentelider_controller.mostrar_logros()


@web.route("/docentelider/publicaciones")
def docente_publicaciones():
    return docentelider_controller.mostrar_publicaciones()


@web.route("/docentelider/ranking")
def docente_ranking():
    return docentelider_controller.mostrar_ranking()


@web.route("/docentelider/perfil")
def docente_perfil():
    return docentelider_controller.mostrar_perfil()


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




DESTINOS = {"ADMIN": "/admin", "ESTUDIANTE": "/estudiante", "DOCENTE": "/docentelider"}


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



@web.route("/docentelider/api/perfil")
def docente_api_perfil():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    # La facultad sale del semillero que lidera el docente
    facultad = db.session.execute(text("""
        SELECT f.nombre
        FROM docentelider d
        JOIN semillero s ON s.id_semillero = d.id_semillero_liderado
        JOIN facultad f ON f.id_facultad = s.id_facultad
        WHERE d.id_usuario = :id
    """), {"id": usuario.id_usuario}).scalar()

    # Última solicitud de cambio por cada dato (pendiente, aprobada o rechazada)
    solicitudes = {}
    historial = (SolicitudActualizacion.query
                 .filter_by(id_usuario=usuario.id_usuario)
                 .order_by(SolicitudActualizacion.fecha_solicitud.desc())
                 .all())
    for s in historial:
        if s.campo_modificado not in solicitudes:
            solicitudes[s.campo_modificado] = {
                "estado": s.estado,
                "valor_nuevo": s.valor_nuevo,
                "motivo_rechazo": s.motivo_rechazo,
            }

    return jsonify({
        "nombre_institucional": usuario.nombre_institucional,
        "correo_institucional": usuario.correo_institucional,
        "foto_perfil": usuario.foto_perfil,
        "facultad": facultad or "Sin facultad asignada",
        "solicitudes": solicitudes,
    })


@web.route("/docentelider/api/perfil/solicitud", methods=["POST"])
def docente_solicitar_cambio():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    datos = request.get_json(silent=True) or {}
    cambios = {}

    nombre = (datos.get("nombre") or "").strip()
    if nombre and nombre != usuario.nombre_institucional:
        if len(nombre) < 3 or len(nombre) > 150:
            return jsonify({
                "mensaje": "El nombre debe tener entre 3 y 150 caracteres."
            }), 400
        cambios["nombre_institucional"] = (usuario.nombre_institucional, nombre)

    correo = (datos.get("correo") or "").strip().lower()
    if correo and correo != usuario.correo_institucional:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
            return jsonify({"mensaje": "El correo no tiene un formato válido."}), 400
        if not correo.endswith("@unilibre.edu.co"):
            return jsonify({
                "mensaje": "Debes utilizar tu correo institucional (@unilibre.edu.co)."
            }), 400
        if Usuario.query.filter_by(correo_institucional=correo).first():
            return jsonify({"mensaje": "Este correo ya está registrado."}), 409
        cambios["correo_institucional"] = (usuario.correo_institucional, correo)

    if not cambios:
        return jsonify({"mensaje": "No hiciste ningún cambio en tus datos."}), 400

    for campo in cambios:
        pendiente = SolicitudActualizacion.query.filter_by(
            id_usuario=usuario.id_usuario,
            campo_modificado=campo,
            estado="PENDIENTE"
        ).first()
        if pendiente:
            return jsonify({
                "mensaje": "Ya tienes una solicitud pendiente para este dato. "
                           "Espera la respuesta del Administrador."
            }), 409

    try:
        for campo, (anterior, nuevo) in cambios.items():
            db.session.add(SolicitudActualizacion(
                id_usuario=usuario.id_usuario,
                campo_modificado=campo,
                valor_anterior=anterior,
                valor_nuevo=nuevo,
                estado="PENDIENTE",
                fecha_solicitud=datetime.now()
            ))
        db.session.commit()
        return jsonify({
            "mensaje": "Tu solicitud fue enviada y está pendiente de aprobación "
                       "del Administrador."
        }), 201
    except Exception as error:
        db.session.rollback()
        print("ERROR AL GUARDAR SOLICITUD DE ACTUALIZACION:", repr(error))
        return jsonify({"mensaje": "No fue posible enviar la solicitud."}), 500


@web.route("/docentelider/api/perfil/contrasena", methods=["POST"])
def docente_cambiar_contrasena():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    datos = request.get_json(silent=True) or {}
    actual = datos.get("actual") or ""
    nueva = datos.get("nueva") or ""
    confirmar = datos.get("confirmar") or ""

    if not check_password_hash(usuario.contrasena_hash, actual):
        return jsonify({"mensaje": "La contraseña actual no es correcta."}), 400
    if len(nueva) < 8:
        return jsonify({
            "mensaje": "La nueva contraseña debe tener mínimo 8 caracteres."
        }), 400
    if nueva != confirmar:
        return jsonify({
            "mensaje": "La confirmación no coincide con la nueva contraseña."
        }), 400
    if check_password_hash(usuario.contrasena_hash, nueva):
        return jsonify({
            "mensaje": "La nueva contraseña debe ser diferente a la actual."
        }), 400

    try:
        usuario.contrasena_hash = generate_password_hash(nueva)
        usuario.fecha_actualizacion = datetime.now()
        db.session.commit()
        return jsonify({"mensaje": "Tu contraseña fue actualizada."})
    except Exception as error:
        db.session.rollback()
        print("ERROR AL CAMBIAR CONTRASENA:", repr(error))
        return jsonify({"mensaje": "No fue posible actualizar la contraseña."}), 500


@web.route("/docentelider/api/perfil/foto", methods=["POST"])
def docente_cambiar_foto():
    usuario = _usuario_actual()
    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    archivo = request.files.get("foto")
    if not archivo or not archivo.filename:
        return jsonify({"mensaje": "Selecciona una imagen."}), 400

    extension = ""
    if "." in archivo.filename:
        extension = archivo.filename.rsplit(".", 1)[-1].lower()
    if extension not in EXTENSIONES_FOTO:
        return jsonify({"mensaje": "Formato no permitido. Usa PNG, JPG o WEBP."}), 400

    archivo.seek(0, os.SEEK_END)
    peso = archivo.tell()
    archivo.seek(0)
    if peso > PESO_MAX_FOTO:
        return jsonify({"mensaje": "La imagen no debe superar 2 MB."}), 400

    carpeta = os.path.join(current_app.static_folder, "uploads", "perfiles")
    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = f"usuario_{usuario.id_usuario}_{int(time.time())}.{extension}"

    try:
        archivo.save(os.path.join(carpeta, nombre_archivo))

        # Borra la foto anterior para no acumular archivos
        anterior = usuario.foto_perfil or ""
        if anterior.startswith("/static/uploads/perfiles/"):
            ruta_anterior = os.path.join(carpeta, os.path.basename(anterior))
            if os.path.exists(ruta_anterior):
                os.remove(ruta_anterior)

        usuario.foto_perfil = f"/static/uploads/perfiles/{nombre_archivo}"
        usuario.fecha_actualizacion = datetime.now()
        db.session.commit()

        return jsonify({
            "mensaje": "Tu foto fue actualizada.",
            "foto_perfil": usuario.foto_perfil
        })
    except Exception as error:
        db.session.rollback()
        print("ERROR AL GUARDAR FOTO:", repr(error))
        return jsonify({"mensaje": "No fue posible guardar la foto."}), 500
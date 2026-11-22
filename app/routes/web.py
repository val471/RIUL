import os
import re
import time
from flask import Blueprint, render_template, current_app
from flask import session, redirect, url_for
from flask import request, jsonify
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


from app.controllers import visitante_controller
from app.controllers import admin_controller
from app.controllers import estudiante_controller
from app.controllers import docentelider_controller
from app.models.usuario import Usuario
from app.models.solicitud_registro import SolicitudRegistro
from app.extensions import db
from datetime import datetime, timedelta
from app.models.solicitud_actualizacion import SolicitudActualizacion


web = Blueprint("web", __name__)
#FOTO PERFIL
EXTENSIONES_FOTO = {"png", "jpg", "jpeg", "webp"}
PESO_MAX_FOTO = 2 * 1024 * 1024  # 2 MB
#EVIDENCIAS
EXTENSIONES_EVIDENCIA = {"pdf", "png"}
PESO_MAX_EVIDENCIA = 5 * 1024 * 1024  # 5 MB


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
@web.before_request
def proteger_panel_estudiante():
    """Solo un usuario con rol ESTUDIANTE puede entrar a /estudiante/..."""
    if (request.path == "/estudiante" or request.path.startswith("/estudiante/")) \
            and session.get("rol") != "ESTUDIANTE":
        return redirect(url_for("web.iniciar_sesion"))

@web.route("/estudiante")
def panel_estudiante():
    return estudiante_controller.mostrar_panel()

# perfil
@web.route("/estudiante/perfil")
def estudiante_perfil():
    return estudiante_controller.mostrar_perfil()


# SEMILLEROS 

@web.route("/estudiante/semilleros")
def explorar_semilleros():
    return render_template("estudiante/semilleros.html")

# PROYECTOS DEL ESTUDIANTE

@web.route("/estudiante/proyectos")
def estudiante_proyectos():
    return render_template("estudiante/proyectos.html")

#  EVENTOS 

@web.route("/estudiante/eventos")
def estudiante_eventos():
    return render_template("estudiante/eventos.html")



# LOGROS
@web.route("/estudiante/logros")
def estudiante_logros():
    return estudiante_controller.mostrar_logros()

@web.route("/estudiante/logros/registrar", methods=["POST"])
def registrar_logro():
    return estudiante_controller.registrar_logro()

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

@web.route("/estudiante/hoja-vida/datos")
def estudiante_hoja_vida_datos():
    return estudiante_controller.obtener_hoja_vida()

def _usuario_actual():
    return db.session.get(Usuario, session.get("id_usuario"))

# PANEL  DOCENTE
@web.before_request
def proteger_panel_docente():
    """Solo un docente líder puede entrar a /docentelider/..."""
    if request.path.startswith("/docentelider") \
            and session.get("rol") != "DOCENTE_LIDER":
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

@web.before_request
def proteger_panel_admin():
    """Solo un usuario con rol ADMIN puede entrar a /admin/..."""
    if (request.path == "/admin" or request.path.startswith("/admin/")) \
            and session.get("rol") != "ADMIN":
        if request.path.startswith("/admin/api"):
            return jsonify({"mensaje": "No autorizado"}), 401
        return redirect(url_for("web.iniciar_sesion"))

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





DESTINOS = {"ADMIN": "/admin", "ESTUDIANTE": "/estudiante", "DOCENTE_LIDER": "/docentelider"}

MAX_INTENTOS = 5
MINUTOS_BLOQUEO = 15
@web.route("/api/login", methods=["POST"])
def api_login():
    datos = request.get_json(silent=True) or {}
    correo = (datos.get("correo") or "").strip().lower()
    clave = datos.get("contrasena") or ""

    usuario = Usuario.query.filter_by(correo_institucional=correo).first()

    # 1. ¿La cuenta está bloqueada temporalmente?
    if usuario and usuario.bloqueado_hasta and usuario.bloqueado_hasta > datetime.now():
        restante = (usuario.bloqueado_hasta - datetime.now()).total_seconds()
        minutos = int(restante // 60) + 1
        return jsonify({
            "mensaje": (
                "Cuenta bloqueada temporalmente por varios intentos fallidos. "
                f"Intenta de nuevo en {minutos} minuto(s)."
            )
        }), 423

    # 2. Credenciales incorrectas
    if (not usuario or usuario.estado != "ACTIVO"
            or not check_password_hash(usuario.contrasena_hash, clave)):

        if usuario and usuario.estado == "ACTIVO":
            usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1

            if usuario.intentos_fallidos >= MAX_INTENTOS:
                usuario.bloqueado_hasta = (
                    datetime.now() + timedelta(minutes=MINUTOS_BLOQUEO)
                )
                usuario.intentos_fallidos = 0

            db.session.commit()

        return jsonify({"mensaje": "Correo o contraseña incorrectos."}), 401

    # 3. Ingreso correcto: se reinicia el contador
    usuario.intentos_fallidos = 0
    usuario.bloqueado_hasta = None
    db.session.commit()

    session.permanent = True
    session["nombre_institucional"] = usuario.nombre_institucional
    session["id_usuario"] = usuario.id_usuario
    session["rol"] = usuario.rol
    return jsonify({
        "mensaje": "Acceso correcto.",
        "redirect": DESTINOS.get(usuario.rol, "/"),
    })


@web.route("/estudiante/api/semilleros")
def estudiante_api_semilleros():
    facultad_estudiante = db.session.execute(text("""
        SELECT p.id_facultad
        FROM estudianteinvestigador ei
        INNER JOIN programa p
            ON p.id_programa = ei.id_programa
        WHERE ei.id_usuario = :id
    """), {"id": session.get("id_usuario")}).scalar()

    filas = db.session.execute(text("""
        SELECT
            s.id_semillero,
            s.id_facultad,
            s.nombre,
            s.descripcion,
            s.linea_investigacion,
            s.cupo_maximo,
            f.nombre AS facultad,
            (
                SELECT COUNT(*)
                FROM membresiasemillero m
                WHERE m.id_semillero = s.id_semillero
                  AND m.fecha_salida IS NULL
            ) AS integrantes,
            (
                SELECT sv.estado
                FROM solicitudvinculacion sv
                WHERE sv.id_estudiante = :estudiante
                  AND sv.id_semillero = s.id_semillero
                ORDER BY sv.fecha_solicitud DESC
                LIMIT 1
            ) AS mi_solicitud
        FROM semillero s
        INNER JOIN facultad f
            ON f.id_facultad = s.id_facultad
        WHERE s.estado = 'ACTIVO'
        ORDER BY s.nombre
    """), {"estudiante": session.get("id_usuario")}).mappings().all()

    return jsonify([{
        "id": f["id_semillero"],
        "nombre": f["nombre"],
        "descripcion": f["descripcion"],
        "linea": f["linea_investigacion"],
        "facultad": f["facultad"],
        "cupo_maximo": f["cupo_maximo"],
        "integrantes": f["integrantes"],
        "mi_solicitud": f["mi_solicitud"],
        "es_mi_facultad": f["id_facultad"] == facultad_estudiante,
    } for f in filas])


@web.route("/api/registro", methods=["POST"])
def api_registro():
    datos = request.get_json(silent=True) or {}

    nombres = (datos.get("nombres") or "").strip()
    apellidos = (datos.get("apellidos") or "").strip()
    correo = (datos.get("correo") or "").strip().lower()
    documento = (datos.get("documento") or "").strip()
    telefono = (datos.get("telefono") or "").strip()
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

    if rol not in ["ESTUDIANTE", "DOCENTE_LIDER"]:
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
            telefono=telefono,
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
#Eventos
@web.route("/estudiante/api/eventos")
def api_eventos_estudiante():

    consulta = text("""
        SELECT
            id_evento,
            nombre,
            descripcion,
            fecha,
            fecha_cierre,
            lugar,
            modalidad,
            CASE
                WHEN fecha_cierre IS NOT NULL
                     AND fecha_cierre >= NOW()
                THEN 'abierto'
                ELSE 'cerrado'
            END AS estado
        FROM evento
        ORDER BY fecha ASC
    """)

    eventos = db.session.execute(consulta).mappings().all()

    resultado = []

    for evento in eventos:
        resultado.append({
            "id_evento": evento["id_evento"],
            "nombre": evento["nombre"],
            "descripcion": evento["descripcion"],
            "fecha": evento["fecha"].strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_cierre": (
                evento["fecha_cierre"].strftime("%Y-%m-%d %H:%M:%S")
                if evento["fecha_cierre"] else None
            ),
            "lugar": evento["lugar"],
            "modalidad": evento["modalidad"],
            "estado": evento["estado"]
        })

    return jsonify(resultado)


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

@web.route("/docentelider/api/registros")
def docente_api_registros():
    id_semillero = _semillero_del_docente()

    if not id_semillero:
        return jsonify([])

    filas = db.session.execute(text("""
        SELECT
            sr.nombre_completo,
            sr.correo_institucional,
            sr.fecha_solicitud,
            p.nombre AS programa
        FROM solicitudregistro sr
        INNER JOIN semillero s
            ON s.id_facultad = sr.id_facultad
        LEFT JOIN programa p
            ON p.id_programa = sr.id_programa
        WHERE s.id_semillero = :semillero
          AND sr.estado = 'PENDIENTE'
          AND sr.rol_solicitado = 'ESTUDIANTE'
        ORDER BY sr.fecha_solicitud
    """), {"semillero": id_semillero}).mappings().all()

    return jsonify([{
        "nombre": f["nombre_completo"],
        "correo": f["correo_institucional"],
        "programa": f["programa"] or "Sin programa",
        "fecha": f["fecha_solicitud"].strftime("%d/%m/%Y"),
    } for f in filas])

@web.route("/admin/api/solicitudes/<int:id_solicitud>/aprobar", methods=["POST"])
def admin_aprobar_solicitud(id_solicitud):
    return admin_controller.aprobar_solicitud_registro(id_solicitud)


@web.route("/admin/api/solicitudes/<int:id_solicitud>/rechazar", methods=["POST"])
def admin_rechazar_solicitud(id_solicitud):
    return admin_controller.rechazar_solicitud_registro(id_solicitud)



# ==============================
# ESTUDIANTE: SOLICITAR VINCULACIÓN A UN SEMILLERO (RF-27, RF-37)
# ==============================

@web.route("/estudiante/api/semilleros/<int:id_semillero>/solicitar",
           methods=["POST"])
def estudiante_solicitar_vinculacion(id_semillero):
    id_estudiante = session.get("id_usuario")

    # 1. El estudiante debe estar activo
    estudiante = db.session.execute(text("""
        SELECT u.estado
        FROM usuario u
        INNER JOIN estudianteinvestigador e
            ON e.id_usuario = u.id_usuario
        WHERE u.id_usuario = :id
    """), {"id": id_estudiante}).mappings().first()

    if not estudiante or estudiante["estado"] != "ACTIVO":
        return jsonify({"mensaje": "Tu cuenta no está activa."}), 403

    # 2. El semillero debe existir y estar activo
    semillero = db.session.execute(text("""
        SELECT
            s.estado,
            s.id_facultad,
            s.cupo_maximo,
            (
                SELECT COUNT(*)
                FROM membresiasemillero m
                WHERE m.id_semillero = s.id_semillero
                  AND m.fecha_salida IS NULL
            ) AS integrantes
        FROM semillero s
        WHERE s.id_semillero = :id
    """), {"id": id_semillero}).mappings().first()

    if not semillero or semillero["estado"] != "ACTIVO":
        return jsonify({"mensaje": "El semillero no está disponible."}), 404

    # 3. Solo puede solicitar vinculación en su propia facultad
    facultad_estudiante = db.session.execute(text("""
        SELECT p.id_facultad
        FROM estudianteinvestigador ei
        INNER JOIN programa p
            ON p.id_programa = ei.id_programa
        WHERE ei.id_usuario = :id
    """), {"id": id_estudiante}).scalar()

    if semillero["id_facultad"] != facultad_estudiante:
        return jsonify({
            "mensaje": (
                "Solo puedes solicitar vinculación a semilleros de tu "
                "facultad. Los de otras facultades puedes seguirlos."
            )
        }), 403

    # 4. El semillero debe tener cupo
    if semillero["integrantes"] >= semillero["cupo_maximo"]:
        return jsonify({"mensaje": "El semillero no tiene cupo disponible."}), 409

    # 5. No puede estar ya en un semillero
    ya_miembro = db.session.execute(text("""
        SELECT 1
        FROM membresiasemillero
        WHERE id_estudiante = :id
          AND fecha_salida IS NULL
    """), {"id": id_estudiante}).first()

    if ya_miembro:
        return jsonify({"mensaje": "Ya perteneces a un semillero."}), 409

    # 6. No puede repetir una solicitud pendiente al mismo semillero
    repetida = db.session.execute(text("""
        SELECT 1
        FROM solicitudvinculacion
        WHERE id_estudiante = :est
          AND id_semillero = :sem
          AND estado = 'PENDIENTE'
    """), {"est": id_estudiante, "sem": id_semillero}).first()

    if repetida:
        return jsonify({
            "mensaje": "Ya tienes una solicitud pendiente en este semillero."
        }), 409

    # 7. Se guarda la solicitud
    try:
        db.session.execute(text("""
            INSERT INTO solicitudvinculacion
                (id_estudiante, id_semillero, estado, fecha_solicitud, tipo)
            VALUES
                (:est, :sem, 'PENDIENTE', NOW(), 'SOLICITUD')
        """), {"est": id_estudiante, "sem": id_semillero})

        db.session.commit()

        return jsonify({"mensaje": "Solicitud enviada. Queda pendiente de respuesta."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL SOLICITAR VINCULACION:", repr(error))
        return jsonify({"mensaje": "No fue posible enviar la solicitud."}), 500

#Seguimiento de semillero estudiante#
@web.route("/estudiante/api/semilleros/<int:id_semillero>/seguir", methods=["POST"])
def estudiante_seguir_semillero(id_semillero):
    id_usuario = session.get("id_usuario")

    if not id_usuario:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    try:
        # Verificar que el semillero exista
        semillero = db.session.execute(text("""
            SELECT id_semillero
            FROM semillero
            WHERE id_semillero = :id
              AND estado = 'ACTIVO'
        """), {"id": id_semillero}).first()

        if not semillero:
            return jsonify({"mensaje": "El semillero no está disponible."}), 404

        # Verificar si ya lo sigue
        existe = db.session.execute(text("""
            SELECT 1
            FROM seguimientoesemillero
            WHERE id_usuario = :usuario
              AND id_semillero = :semillero
        """), {
            "usuario": id_usuario,
            "semillero": id_semillero
        }).first()

        if existe:
            return jsonify({"mensaje": "Ya sigues este semillero."}), 409

        # Registrar seguimiento
        db.session.execute(text("""
            INSERT INTO seguimientosemillero
                (id_usuario, id_semillero, fecha_seguimiento)
            VALUES (:usuario, :semillero, NOW())
        """), {
            "usuario": id_usuario,
            "semillero": id_semillero
        })

        db.session.commit()

        return jsonify({"mensaje": "Ahora sigues este semillero."}), 200

    except Exception as error:
        db.session.rollback()
        print("ERROR AL SEGUIR SEMILLERO:", repr(error))
        return jsonify({"mensaje": "No fue posible seguir el semillero."}), 500

# PROYECTOS DEL ESTUDIANTE
@web.route("/estudiante/api/proyectos")
def estudiante_api_proyectos():
    id_estudiante = session.get("id_usuario")

    if not id_estudiante:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    try:
        proyectos = db.session.execute(text("""
            SELECT
                p.id_proyecto,
                p.titulo,
                p.descripcion,
                p.fecha_inicio,
                p.estado,
                s.nombre AS semillero,
                (
                    SELECT COUNT(*)
                    FROM avanceproyecto a
                    WHERE a.id_proyecto = p.id_proyecto
                ) AS total_avances
            FROM membresiasemillero m
            INNER JOIN proyecto p
                ON p.id_semillero = m.id_semillero
            INNER JOIN semillero s
                ON s.id_semillero = p.id_semillero
            WHERE m.id_estudiante = :id
              AND m.fecha_salida IS NULL
            ORDER BY p.fecha_inicio DESC
        """), {"id": id_estudiante}).mappings().all()

        return jsonify([{
            "id": p["id_proyecto"],
            "titulo": p["titulo"],
            "descripcion": p["descripcion"] or "",
            "fecha_inicio": p["fecha_inicio"].strftime("%d/%m/%Y"),
            "estado": p["estado"],
            "semillero": p["semillero"],
            "total_avances": p["total_avances"]
        } for p in proyectos])

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CONSULTAR PROYECTOS:", repr(error))
        return jsonify({"mensaje": "No fue posible consultar los proyectos."}), 500
    

@web.route("/docentelider/api/semillero")
def docente_api_semillero():
    id_semillero = _semillero_del_docente()

    if not id_semillero:
        return jsonify({"asignado": False})

    s = db.session.execute(text("""
        SELECT
            s.nombre,
            s.descripcion,
            s.linea_investigacion,
            s.estado,
            s.cupo_maximo,
            f.nombre AS facultad,
            (
                SELECT COUNT(*)
                FROM membresiasemillero m
                WHERE m.id_semillero = s.id_semillero
                  AND m.fecha_salida IS NULL
            ) AS integrantes,
            (
                SELECT COUNT(*)
                FROM proyecto p
                WHERE p.id_semillero = s.id_semillero
            ) AS proyectos
        FROM semillero s
        INNER JOIN facultad f
            ON f.id_facultad = s.id_facultad
        WHERE s.id_semillero = :id
    """), {"id": id_semillero}).mappings().first()

    if not s:
        return jsonify({"asignado": False})

    return jsonify({
        "asignado": True,
        "nombre": s["nombre"],
        "descripcion": s["descripcion"],
        "linea": s["linea_investigacion"],
        "estado": s["estado"],
        "cupo_maximo": s["cupo_maximo"],
        "facultad": s["facultad"],
        "integrantes": s["integrantes"],
        "proyectos": s["proyectos"],
    })

def _resolver_vinculacion(id_solicitud, aceptar):
    id_docente = session.get("id_usuario") 

    if not id_docente:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    try:
        # Buscar la solicitud
        solicitud = db.session.execute(text("""
            SELECT
                id_estudiante,
                id_semillero,
                estado,
                tipo
            FROM solicitudvinculacion
            WHERE id_solicitud_vinc = :id
        """), {"id": id_solicitud}).mappings().first()

        if not solicitud:
            return jsonify({"mensaje": "La solicitud no existe."}), 404

        if solicitud["estado"] != "PENDIENTE":
            return jsonify({"mensaje": "La solicitud ya fue resuelta."}), 409

        # Verificar que el semillero pertenezca al docente
        semillero = db.session.execute(text("""
            SELECT id_semillero_liderado
            FROM docentelider
            WHERE id_usuario = :docente
        """), {"docente": id_docente}).scalar()

        if semillero != solicitud["id_semillero"]:
            return jsonify({
                "mensaje": "No puedes resolver solicitudes de otro semillero."
            }), 403

        if aceptar:
            # Verificar que el estudiante no pertenezca a otro semillero
            miembro = db.session.execute(text("""
                SELECT 1
                FROM membresiasemillero
                WHERE id_estudiante = :estudiante
                  AND fecha_salida IS NULL
            """), {"estudiante": solicitud["id_estudiante"]}).first()

            if miembro:
                return jsonify({
                    "mensaje": "El estudiante ya pertenece a un semillero."
                }), 409

            # Verificar cupo
            cupo = db.session.execute(text("""
                SELECT
                    s.cupo_maximo,
                    (
                        SELECT COUNT(*)
                        FROM membresiasemillero m
                        WHERE m.id_semillero = s.id_semillero
                          AND m.fecha_salida IS NULL
                    ) AS integrantes
                FROM semillero s
                WHERE s.id_semillero = :semillero
            """), {"semillero": semillero}).mappings().first()

            if not cupo or cupo["integrantes"] >= cupo["cupo_maximo"]:
                return jsonify({
                    "mensaje": "El semillero no tiene cupos disponibles."
                }), 409

            # Registrar membresia
            db.session.execute(text("""
                INSERT INTO membresiasemillero
                    (id_estudiante, id_semillero, fecha_ingreso)
                VALUES
                    (:estudiante, :semillero, NOW())
            """), {
                "estudiante": solicitud["id_estudiante"],
                "semillero": semillero
            })

            nuevo_estado = "APROBADA"

        else:
            nuevo_estado = "RECHAZADA"

        # Actualizar solicitud
        db.session.execute(text("""
            UPDATE solicitudvinculacion
            SET estado = :estado,
                id_docente_revisor = :docente,
                fecha_resolucion = NOW()
            WHERE id_solicitud_vinc = :id
        """), {
            "estado": nuevo_estado,
            "docente": id_docente,
            "id": id_solicitud
        }) 

        db.session.commit()

        return jsonify({
            "mensaje": (
                "Solicitud aprobada correctamente."
                if aceptar else "Solicitud rechazada correctamente."
            )
        }), 200

    except Exception as error:
        db.session.rollback()
        print("ERROR AL RESOLVER VINCULACION:", repr(error))
        return jsonify({
            "mensaje": "No fue posible resolver la solicitud."
        }), 500

@web.route("/docentelider/api/vinculaciones/<int:id_solicitud>/aceptar",
           methods=["POST"])
def docente_aceptar_vinculacion(id_solicitud):
    return _resolver_vinculacion(id_solicitud, True)


@web.route("/docentelider/api/vinculaciones/<int:id_solicitud>/rechazar",
           methods=["POST"])
def docente_rechazar_vinculacion(id_solicitud):
    return _resolver_vinculacion(id_solicitud, False)

# ==============================
# ADMIN: CREAR CONVOCATORIA (RF-02)
# ==============================

@web.route("/admin/api/convocatorias", methods=["POST"])
def admin_crear_convocatoria():
    datos = request.get_json(silent=True) or {}

    titulo = (datos.get("titulo") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    modalidad = datos.get("modalidad")

    if not titulo:
        return jsonify({"mensaje": "El título es obligatorio."}), 400

    if len(titulo) > 150:
        return jsonify({
            "mensaje": "El título no puede superar los 150 caracteres."
        }), 400

    if modalidad not in ("semillero", "individual", "ambas"):
        return jsonify({"mensaje": "Selecciona una modalidad de participación."}), 400

    try:
        inicio = datetime.strptime(datos.get("fecha_inicio") or "", "%Y-%m-%d").date()
        cierre = datetime.strptime(datos.get("fecha_cierre") or "", "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "mensaje": "Las fechas de inicio y de cierre son obligatorias."
        }), 400

    if cierre < inicio:
        return jsonify({
            "mensaje": "La fecha de cierre no puede ser anterior a la fecha de inicio."
        }), 400

    id_admin = session.get("id_usuario")

    try:
        db.session.execute(text("""
            INSERT IGNORE INTO administrador (id_usuario) VALUES (:id)
        """), {"id": id_admin})

        nueva = db.session.execute(text("""
            INSERT INTO convocatoria
                (titulo, descripcion, fecha_inicio, fecha_cierre,
                 modalidad, estado, id_admin_creador, fecha_actualizacion)
            VALUES
                (:titulo, :descripcion, :inicio, :cierre,
                 :modalidad, 'ACTIVA', :admin, NOW())
        """), {
            "titulo": titulo,
            "descripcion": descripcion or None,
            "inicio": inicio,
            "cierre": cierre,
            "modalidad": modalidad,
            "admin": id_admin
        })

        db.session.execute(text("""
            INSERT INTO historial
                (id_usuario, accion, tabla_afectada, id_registro,
                 valor_anterior, valor_nuevo, fecha)
            VALUES
                (:usuario, 'CREAR_CONVOCATORIA', 'convocatoria', :registro,
                 NULL, :nuevo, NOW())
        """), {
            "usuario": id_admin,
            "registro": nueva.lastrowid,
            "nuevo": titulo
        })

        db.session.commit()

        return jsonify({"mensaje": "Convocatoria creada correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CREAR CONVOCATORIA:", repr(error))
        return jsonify({"mensaje": "No fue posible crear la convocatoria."}), 500

    # ==============================
# ADMIN: VER, EDITAR Y ELIMINAR CONVOCATORIA (RF-02)
# ==============================

def _leer_convocatoria(datos):
    """Valida los datos del formulario. Devuelve (valores, mensaje_de_error)."""
    titulo = (datos.get("titulo") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    modalidad = datos.get("modalidad")

    if not titulo:
        return None, "El título es obligatorio."

    if len(titulo) > 150:
        return None, "El título no puede superar los 150 caracteres."

    if modalidad not in ("semillero", "individual", "ambas"):
        return None, "Selecciona una modalidad de participación."

    try:
        inicio = datetime.strptime(datos.get("fecha_inicio") or "", "%Y-%m-%d").date()
        cierre = datetime.strptime(datos.get("fecha_cierre") or "", "%Y-%m-%d").date()
    except ValueError:
        return None, "Las fechas de inicio y de cierre son obligatorias."

    if cierre < inicio:
        return None, "La fecha de cierre no puede ser anterior a la fecha de inicio."

    return {
        "titulo": titulo,
        "descripcion": descripcion or None,
        "inicio": inicio,
        "cierre": cierre,
        "modalidad": modalidad
    }, None


def _buscar_convocatoria(id_convocatoria):
    return db.session.execute(text("""
        SELECT id_convocatoria, titulo, descripcion,
               fecha_inicio, fecha_cierre, modalidad
        FROM convocatoria
        WHERE id_convocatoria = :id
    """), {"id": id_convocatoria}).mappings().first()


def _resumen_convocatoria(titulo, modalidad, inicio, cierre):
    return f"{titulo} | {modalidad} | {inicio} a {cierre}"


@web.route("/admin/api/convocatorias/<int:id_convocatoria>")
def admin_ver_convocatoria(id_convocatoria):
    c = _buscar_convocatoria(id_convocatoria)

    if not c:
        return jsonify({"mensaje": "La convocatoria no existe."}), 404

    return jsonify({
        "titulo": c["titulo"],
        "descripcion": c["descripcion"] or "",
        "fecha_inicio": c["fecha_inicio"].isoformat(),
        "fecha_cierre": c["fecha_cierre"].isoformat(),
        "modalidad": c["modalidad"],
    })


@web.route("/admin/api/convocatorias/<int:id_convocatoria>", methods=["PUT"])
def admin_editar_convocatoria(id_convocatoria):
    anterior = _buscar_convocatoria(id_convocatoria)

    if not anterior:
        return jsonify({"mensaje": "La convocatoria no existe."}), 404

    valores, error = _leer_convocatoria(request.get_json(silent=True) or {})

    if error:
        return jsonify({"mensaje": error}), 400

    try:
        db.session.execute(text("""
            UPDATE convocatoria
            SET titulo = :titulo,
                descripcion = :descripcion,
                fecha_inicio = :inicio,
                fecha_cierre = :cierre,
                modalidad = :modalidad,
                fecha_actualizacion = NOW()
            WHERE id_convocatoria = :id
        """), {**valores, "id": id_convocatoria})

        db.session.execute(text("""
            INSERT INTO historial
                (id_usuario, accion, tabla_afectada, id_registro,
                 valor_anterior, valor_nuevo, fecha)
            VALUES
                (:usuario, 'EDITAR_CONVOCATORIA', 'convocatoria', :registro,
                 :anterior, :nuevo, NOW())
        """), {
            "usuario": session.get("id_usuario"),
            "registro": id_convocatoria,
            "anterior": _resumen_convocatoria(
                anterior["titulo"], anterior["modalidad"],
                anterior["fecha_inicio"], anterior["fecha_cierre"]
            ),
            "nuevo": _resumen_convocatoria(
                valores["titulo"], valores["modalidad"],
                valores["inicio"], valores["cierre"]
            )
        })

        db.session.commit()

        return jsonify({"mensaje": "Convocatoria actualizada correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL EDITAR CONVOCATORIA:", repr(error))
        return jsonify({"mensaje": "No fue posible actualizar la convocatoria."}), 500


@web.route("/admin/api/convocatorias/<int:id_convocatoria>", methods=["DELETE"])
def admin_eliminar_convocatoria(id_convocatoria):
    anterior = _buscar_convocatoria(id_convocatoria)

    if not anterior:
        return jsonify({"mensaje": "La convocatoria no existe."}), 404

    con_inscripciones = db.session.execute(text("""
        SELECT 1
        FROM inscripcionconvocatoria
        WHERE id_convocatoria = :id
        LIMIT 1
    """), {"id": id_convocatoria}).first()

    if con_inscripciones:
        return jsonify({
            "mensaje": "No se puede eliminar: la convocatoria ya tiene inscripciones."
        }), 409

    try:
        db.session.execute(text("""
            DELETE FROM convocatoria WHERE id_convocatoria = :id
        """), {"id": id_convocatoria})

        db.session.execute(text("""
            INSERT INTO historial
                (id_usuario, accion, tabla_afectada, id_registro,
                 valor_anterior, valor_nuevo, fecha)
            VALUES
                (:usuario, 'ELIMINAR_CONVOCATORIA', 'convocatoria', :registro,
                 :anterior, NULL, NOW())
        """), {
            "usuario": session.get("id_usuario"),
            "registro": id_convocatoria,
            "anterior": _resumen_convocatoria(
                anterior["titulo"], anterior["modalidad"],
                anterior["fecha_inicio"], anterior["fecha_cierre"]
            )
        })

        db.session.commit()

        return jsonify({"mensaje": "Convocatoria eliminada."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL ELIMINAR CONVOCATORIA:", repr(error))
        return jsonify({"mensaje": "No fue posible eliminar la convocatoria."}), 500


def _semillero_del_docente():
    id_usuario = session.get("id_usuario")

    if not id_usuario:
        return None

    resultado = db.session.execute(text("""
        SELECT id_semillero_liderado
        FROM docentelider
        WHERE id_usuario = :id
    """), {"id": id_usuario}).scalar()

    return resultado

@web.route("/estudiante/api/perfil/solicitud", methods=["POST"])
def estudiante_solicitar_cambio_perfil():
    return estudiante_controller.solicitar_cambio_perfil()

@web.route("/estudiante/api/perfil/solicitud-foto", methods=["POST"])
def estudiante_solicitar_cambio_foto():
    return estudiante_controller.solicitar_cambio_foto()

@web.route("/estudiante/api/notificaciones")
def estudiante_api_notificaciones():
    id_usuario = session.get("id_usuario")

    filas = db.session.execute(text("""
        SELECT
            id_notificacion,
            mensaje,
            tipo,
            estado,
            TIMESTAMPDIFF(MINUTE, fecha, NOW()) AS minutos
        FROM notificacion
        WHERE id_usuario = :id
        ORDER BY fecha DESC, id_notificacion DESC
        LIMIT 20
    """), {"id": id_usuario}).mappings().all()

    no_leidas = db.session.execute(text("""
        SELECT COUNT(*)
        FROM notificacion
        WHERE id_usuario = :id
          AND estado = 0
    """), {"id": id_usuario}).scalar()

    return jsonify({
        "no_leidas": no_leidas,
        "notificaciones": [{
            "id": f["id_notificacion"],
            "mensaje": f["mensaje"],
            "tipo": f["tipo"],
            "leida": bool(f["estado"]),
            "minutos": max(f["minutos"] or 0, 0),
        } for f in filas]
    })


@web.route("/estudiante/api/notificaciones/leidas", methods=["POST"])
def estudiante_marcar_notificaciones_leidas():
    try:
        db.session.execute(text("""
            UPDATE notificacion
            SET estado = 1
            WHERE id_usuario = :id
              AND estado = 0
        """), {"id": session.get("id_usuario")})

        db.session.commit()

        return jsonify({"mensaje": "Notificaciones marcadas como leídas."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL MARCAR NOTIFICACIONES:", repr(error))
        return jsonify({
            "mensaje": "No fue posible actualizar las notificaciones."
        }), 500

@web.route("/estudiante/api/perfil/contrasena", methods=["POST"])
def estudiante_cambiar_contrasena():
    return estudiante_controller.cambiar_contrasena()

@web.route("/admin/solicitudes/actualizaciones")
def admin_solicitudes_actualizaciones():
    solicitudes = admin_controller.mostrar_solicitudes_actualizacion()

    return jsonify([
        {
            "id": s["id_solicitud_act"],
            "nombre": s["nombre_institucional"],
            "correo": s["correo_institucional"],
            "campo": s["campo_modificado"],
            "valor_anterior": s["valor_anterior"],
            "valor_nuevo": s["valor_nuevo"],
            "descripcion": s["descripcion_solicitud"],
            "fecha": s["fecha_solicitud"].strftime("%d/%m/%Y %H:%M")
        }
        for s in solicitudes
    ])
@web.route(
    "/admin/solicitudes/actualizaciones/<int:id_solicitud>/aprobar",
    methods=["POST"]
)
def admin_aprobar_solicitud_actualizacion(id_solicitud):
    return admin_controller.aprobar_solicitud_actualizacion(
        id_solicitud
    )
@web.route(
    "/admin/solicitudes/actualizaciones/<int:id_solicitud>/rechazar",
    methods=["POST"]
)
def admin_rechazar_solicitud_actualizacion(id_solicitud):

    datos = request.get_json(silent=True) or {}
    motivo = datos.get("motivo", "").strip()

    if not motivo:
        return jsonify({
            "mensaje": "Debes indicar el motivo del rechazo."
        }), 400

    return admin_controller.rechazar_solicitud_actualizacion(
        id_solicitud,
        motivo
    )

@web.route("/admin/api/notificaciones")
def admin_api_notificaciones():
    """Notificaciones del administrador: todo lo que espera su decision."""
    consultas = [
        ("REGISTRO", "solicitudes", """
            SELECT CONCAT('Nueva solicitud de registro: ', nombre_completo,
                          ' (', rol_solicitado, ')') AS mensaje,
                   TIMESTAMPDIFF(MINUTE, fecha_solicitud, NOW()) AS minutos
            FROM solicitudregistro
            WHERE estado = 'PENDIENTE'
            ORDER BY fecha_solicitud DESC LIMIT 10"""),
        ("ACTUALIZACION", "solicitudes", """
            SELECT CONCAT(u.nombre_institucional,
                          ' solicita actualizar: ', sa.campo_modificado) AS mensaje,
                   TIMESTAMPDIFF(MINUTE, sa.fecha_solicitud, NOW()) AS minutos
            FROM solicitudactualizacion sa
            JOIN usuario u ON u.id_usuario = sa.id_usuario
            WHERE sa.estado = 'PENDIENTE'
            ORDER BY sa.fecha_solicitud DESC LIMIT 10"""),
        ("LIDERAZGO", "solicitudes", """
            SELECT CONCAT('Un docente solicita liderar el semillero ',
                          s.nombre) AS mensaje,
                   TIMESTAMPDIFF(MINUTE, sl.fecha_solicitud, NOW()) AS minutos
            FROM solicitudliderazgo sl
            JOIN semillero s ON s.id_semillero = sl.id_semillero
            WHERE sl.estado = 'PENDIENTE'
            ORDER BY sl.fecha_solicitud DESC LIMIT 10"""),
        ("LOGRO", "logros", """
            SELECT CONCAT('Logro pendiente de validar: ',
                          COALESCE(tl.nombre, 'Logro')) AS mensaje,
                   TIMESTAMPDIFF(MINUTE, l.fecha_registro, NOW()) AS minutos
            FROM logro l
            LEFT JOIN tipologro tl ON tl.id_tipo_logro = l.id_tipo_logro
            WHERE l.estado = 'PENDIENTE'
            ORDER BY l.fecha_registro DESC LIMIT 10"""),
    ]

    items = []
    errores = []
    for tipo, destino, sql in consultas:
        try:
            for fila in db.session.execute(text(sql)).mappings().all():
                items.append({
                    "tipo": tipo,
                    "destino": destino,
                    "mensaje": fila["mensaje"],
                    "minutos": max(fila["minutos"] or 0, 0),
                })
        except Exception as error:
            db.session.rollback()
            print("ERROR NOTIFICACIONES ADMIN (" + tipo + "):", repr(error))
            errores.append(tipo)

    items.sort(key=lambda n: n["minutos"])
    return jsonify({
        "total": len(items),
        "notificaciones": items[:20],
        "errores": errores,
    })
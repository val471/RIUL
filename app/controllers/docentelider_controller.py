
from flask import render_template, jsonify, session, request, current_app
from sqlalchemy import text
from app.extensions import db
import os
import re
import time
from datetime import datetime
from werkzeug.security import ( check_password_hash,  generate_password_hash)
from app.models.usuario import Usuario
from app.models.solicitud_actualizacion import SolicitudActualizacion



def mostrar_panel():
    return render_template("docente_lider/index.html")


def mostrar_semillero():
    return render_template("docente_lider/semilleros.html")


def mostrar_usuarios():
    return render_template("docente_lider/usuario.html")


def mostrar_solicitudes():
    return render_template("docente_lider/solicitudes.html")


def mostrar_proyectos():
    return render_template("docente_lider/proyectos.html")


def mostrar_convocatorias():
    return render_template("docente_lider/convocatorias.html")


def mostrar_eventos():
    return render_template("docente_lider/eventos.html")


def mostrar_publicaciones():
    return render_template("docente_lider/publicaciones.html")


def mostrar_ranking():
    return render_template("docente_lider/ranking.html")


def mostrar_logros():
    return render_template("docente_lider/logros.html")


def mostrar_perfil():
    return render_template("docente_lider/perfil.html")



def _usuario_actual():
    return db.session.get(Usuario, session.get("id_usuario"))


def obtener_perfil():
    usuario = _usuario_actual()

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    facultad = db.session.execute(text("""
        SELECT f.nombre
        FROM docentelider d
        JOIN semillero s
            ON s.id_semillero = d.id_semillero_liderado
        JOIN facultad f
            ON f.id_facultad = s.id_facultad
        WHERE d.id_usuario = :id
    """), {"id": usuario.id_usuario}).scalar()

    solicitudes = {}

    historial = (
        SolicitudActualizacion.query
        .filter_by(id_usuario=usuario.id_usuario)
        .order_by(SolicitudActualizacion.fecha_solicitud.desc())
        .all()
    )

    for s in historial:
        if s.campo_modificado not in solicitudes:
            solicitudes[s.campo_modificado] = {
                "estado": s.estado,
                "valor_nuevo": s.valor_nuevo,
                "motivo_rechazo": s.motivo_rechazo
            }

    return jsonify({
        "nombre_institucional": usuario.nombre_institucional,
        "correo_institucional": usuario.correo_institucional,
        "foto_perfil": usuario.foto_perfil,
        "facultad": facultad or "Sin facultad asignada",
        "solicitudes": solicitudes
    })


def solicitar_cambio_perfil():
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

        cambios["nombre_institucional"] = (
            usuario.nombre_institucional, nombre
        )

    correo = (datos.get("correo") or "").strip().lower()

    if correo and correo != usuario.correo_institucional:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", correo):
            return jsonify({
                "mensaje": "El correo no tiene un formato válido."
            }), 400

        if not correo.endswith("@unilibre.edu.co"):
            return jsonify({
                "mensaje": "Debes utilizar tu correo institucional (@unilibre.edu.co)."
            }), 400

        if Usuario.query.filter_by(correo_institucional=correo).first():
            return jsonify({
                "mensaje": "Este correo ya está registrado."
            }), 409

        cambios["correo_institucional"] = (
            usuario.correo_institucional, correo
        )

    if not cambios:
        return jsonify({
            "mensaje": "No hiciste ningún cambio en tus datos."
        }), 400

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

        return jsonify({
            "mensaje": "No fue posible enviar la solicitud."
        }), 500


def cambiar_contrasena():
    usuario = _usuario_actual()

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    datos = request.get_json(silent=True) or {}

    actual = datos.get("actual") or ""
    nueva = datos.get("nueva") or ""
    confirmar = datos.get("confirmar") or ""

    if not check_password_hash(usuario.contrasena_hash, actual):
        return jsonify({
            "mensaje": "La contraseña actual no es correcta."
        }), 400

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

        return jsonify({
            "mensaje": "Tu contraseña fue actualizada."
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CAMBIAR CONTRASENA:", repr(error))

        return jsonify({
            "mensaje": "No fue posible actualizar la contraseña."
        }), 500


def cambiar_foto():
    usuario = _usuario_actual()

    if not usuario:
        return jsonify({"mensaje": "Usuario no encontrado."}), 404

    archivo = request.files.get("foto")

    if not archivo or not archivo.filename:
        return jsonify({"mensaje": "Selecciona una imagen."}), 400

    extension = ""

    if "." in archivo.filename:
        extension = archivo.filename.rsplit(".", 1)[-1].lower()

    if extension not in {"png", "jpg", "jpeg", "webp"}:
        return jsonify({
            "mensaje": "Formato no permitido. Usa PNG, JPG o WEBP."
        }), 400

    archivo.seek(0, os.SEEK_END)
    peso = archivo.tell()
    archivo.seek(0)

    if peso > 2 * 1024 * 1024:
        return jsonify({
            "mensaje": "La imagen no debe superar 2 MB."
        }), 400

    carpeta = os.path.join(
        current_app.static_folder,
        "uploads",
        "perfiles"
    )

    os.makedirs(carpeta, exist_ok=True)

    nombre_archivo = (
        f"usuario_{usuario.id_usuario}_{int(time.time())}.{extension}"
    )

    try:
        archivo.save(os.path.join(carpeta, nombre_archivo))

        anterior = usuario.foto_perfil or ""

        if anterior.startswith("/static/uploads/perfiles/"):
            ruta_anterior = os.path.join(
                carpeta,
                os.path.basename(anterior)
            )

            if os.path.exists(ruta_anterior):
                os.remove(ruta_anterior)

        usuario.foto_perfil = (
            f"/static/uploads/perfiles/{nombre_archivo}"
        )

        usuario.fecha_actualizacion = datetime.now()

        db.session.commit()

        return jsonify({
            "mensaje": "Tu foto fue actualizada.",
            "foto_perfil": usuario.foto_perfil
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL GUARDAR FOTO:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar la foto."
        }), 500

def _obtener_semillero_del_docente():
    id_usuario = session.get("id_usuario")

    if not id_usuario:
        return None

    return db.session.execute(text("""
        SELECT id_semillero_liderado
        FROM docentelider
        WHERE id_usuario = :id
    """), {"id": id_usuario}).scalar()


def obtener_semillero():
    id_semillero = _obtener_semillero_del_docente()

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


def obtener_integrantes():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify([])

    filas = db.session.execute(text("""
        SELECT
            u.nombre_institucional AS nombre,
            u.correo_institucional AS correo,
            p.nombre AS programa,
            e.semestre,
            n.nombre AS nivel,
            m.fecha_ingreso
        FROM membresiasemillero m
        INNER JOIN estudianteinvestigador e
            ON e.id_usuario = m.id_estudiante
        INNER JOIN usuario u
            ON u.id_usuario = e.id_usuario
        LEFT JOIN programa p
            ON p.id_programa = e.id_programa
        LEFT JOIN nivel n
            ON n.id_nivel = e.id_nivel_actual
        WHERE m.id_semillero = :id
          AND m.fecha_salida IS NULL
        ORDER BY u.nombre_institucional
    """), {"id": id_semillero}).mappings().all()

    return jsonify([{
        "nombre": f["nombre"],
        "correo": f["correo"],
        "programa": f["programa"] or "Sin programa",
        "semestre": f["semestre"],
        "nivel": f["nivel"] or "Sin nivel",
        "ingreso": f["fecha_ingreso"].strftime("%d/%m/%Y")
                   if f["fecha_ingreso"] else "",
    } for f in filas])


def obtener_registros():
    id_semillero = _obtener_semillero_del_docente()

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


def obtener_vinculaciones():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify([])

    filas = db.session.execute(text("""
        SELECT
            sv.id_solicitud_vinc,
            u.nombre_institucional AS nombre,
            p.nombre AS programa,
            e.semestre,
            sv.fecha_solicitud
        FROM solicitudvinculacion sv
        INNER JOIN estudianteinvestigador e
            ON e.id_usuario = sv.id_estudiante
        INNER JOIN usuario u
            ON u.id_usuario = sv.id_estudiante
        LEFT JOIN programa p
            ON p.id_programa = e.id_programa
        WHERE sv.id_semillero = :semillero
          AND sv.estado = 'PENDIENTE'
        ORDER BY sv.fecha_solicitud
    """), {"semillero": id_semillero}).mappings().all()

    return jsonify([{
        "id": f["id_solicitud_vinc"],
        "nombre": f["nombre"],
        "programa": f["programa"] or "Sin programa",
        "semestre": f["semestre"],
        "fecha": f["fecha_solicitud"].strftime("%d/%m/%Y"),
    } for f in filas])



def _resolver_vinculacion(id_solicitud, aceptar):
    id_docente = session.get("id_usuario")

    if not id_docente:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    try:
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

        semillero = _obtener_semillero_del_docente()

        if semillero != solicitud["id_semillero"]:
            return jsonify({
                "mensaje": "No puedes resolver solicitudes de otro semillero."
            }), 403

        if aceptar:
            miembro = db.session.execute(text("""
                SELECT 1
                FROM membresiasemillero
                WHERE id_estudiante = :estudiante
                  AND fecha_salida IS NULL
            """), {
                "estudiante": solicitud["id_estudiante"]
            }).first()

            if miembro:
                return jsonify({
                    "mensaje": "El estudiante ya pertenece a un semillero."
                }), 409

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
            """), {
                "semillero": semillero
            }).mappings().first()

            if not cupo or cupo["integrantes"] >= cupo["cupo_maximo"]:
                return jsonify({
                    "mensaje": "El semillero no tiene cupos disponibles."
                }), 409

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


def aceptar_vinculacion(id_solicitud):
    return _resolver_vinculacion(id_solicitud, True)


def rechazar_vinculacion(id_solicitud):
    return _resolver_vinculacion(id_solicitud, False)



# ==========================================
# PROYECTOS DEL DOCENTE LIDER
# ==========================================

def obtener_proyectos():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify([])

    filas = db.session.execute(text("""
        SELECT
            p.id_proyecto,
            p.titulo,
            p.descripcion,
            p.fecha_inicio,
            p.estado,
            (
                SELECT COUNT(*)
                FROM avanceproyecto a
                WHERE a.id_proyecto = p.id_proyecto
            ) AS avances
        FROM proyecto p
        WHERE p.id_semillero = :id
        ORDER BY p.fecha_inicio DESC, p.id_proyecto DESC
    """), {"id": id_semillero}).mappings().all()

    return jsonify([{
        "id": f["id_proyecto"],
        "titulo": f["titulo"],
        "descripcion": f["descripcion"] or "",
        "inicio": f["fecha_inicio"].strftime("%d/%m/%Y")
                  if f["fecha_inicio"] else "",
        "estado": f["estado"],
        "avances": f["avances"],
    } for f in filas])


def crear_proyecto():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify({
            "mensaje": "No tienes un semillero asignado."
        }), 400

    datos = request.get_json(silent=True) or {}
    titulo = (datos.get("titulo") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()
    inicio = (datos.get("inicio") or "").strip()

    if not titulo:
        return jsonify({"mensaje": "El título es obligatorio."}), 400

    if len(titulo) > 150:
        return jsonify({
            "mensaje": "El título no puede pasar de 150 caracteres."
        }), 400

    try:
        fecha_inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "mensaje": "La fecha de inicio no es válida."
        }), 400

    try:
        db.session.execute(text("""
            INSERT INTO proyecto
                (titulo, descripcion, id_semillero,
                 fecha_inicio, estado, fecha_actualizacion)
            VALUES
                (:titulo, :descripcion, :semillero,
                 :inicio, 'Activo', NOW())
        """), {
            "titulo": titulo,
            "descripcion": descripcion or None,
            "semillero": id_semillero,
            "inicio": fecha_inicio,
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Proyecto cargado correctamente."
        }), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR CARGAR PROYECTO:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar el proyecto."
        }), 500


# ==============================
# APROBAR / RECHAZAR SOLICITUDES DE REGISTRO (RF-01)
# ==============================

def _buscar_solicitud_registro(id_solicitud):
    return db.session.execute(text("""
        SELECT
            id_solicitud,
            nombre_completo,
            correo_institucional,
            documento,
            fecha_nacimiento,
            contrasena_hash,
            rol_solicitado,
            id_programa,
            estado
        FROM solicitudregistro
        WHERE id_solicitud = :id
    """), {"id": id_solicitud}).mappings().first()


def _registrar_historial(accion, id_registro, anterior, nuevo):
    db.session.execute(text("""
        INSERT INTO historial
            (id_usuario, accion, tabla_afectada, id_registro,
             valor_anterior, valor_nuevo, fecha)
        VALUES
            (:usuario, :accion, 'solicitudregistro', :registro,
             :anterior, :nuevo, NOW())
    """), {
        "usuario": session.get("id_usuario"),
        "accion": accion,
        "registro": id_registro,
        "anterior": anterior,
        "nuevo": nuevo
    })


def _asegurar_administrador():
    # id_admin_revisor apunta a la tabla administrador
    db.session.execute(text("""
        INSERT IGNORE INTO administrador (id_usuario) VALUES (:id)
    """), {"id": session.get("id_usuario")})


def aprobar_solicitud_registro(id_solicitud):
    solicitud = _buscar_solicitud_registro(id_solicitud)

    if not solicitud:
        return jsonify({"mensaje": "La solicitud no existe."}), 404

    if solicitud["estado"] != "PENDIENTE":
        return jsonify({"mensaje": "Esta solicitud ya fue resuelta."}), 409

    rol = solicitud["rol_solicitado"]
    documento = solicitud["documento"]

    if rol not in ("ESTUDIANTE", "DOCENTE_LIDER"):
        return jsonify({"mensaje": "El rol solicitado no es válido."}), 400

    if not solicitud["contrasena_hash"]:
        return jsonify({
            "mensaje": "La solicitud no tiene contraseña registrada."
        }), 400

    if not documento:
        return jsonify({
            "mensaje": "La solicitud no tiene documento de identidad."
        }), 400

    if rol == "ESTUDIANTE" and not solicitud["id_programa"]:
        return jsonify({
            "mensaje": "La solicitud del estudiante no tiene programa."
        }), 400

    correo_repetido = db.session.execute(text("""
        SELECT 1 FROM usuario WHERE correo_institucional = :correo
    """), {"correo": solicitud["correo_institucional"]}).first()

    if correo_repetido:
        return jsonify({"mensaje": "Ya existe una cuenta con este correo."}), 409

    if rol == "ESTUDIANTE":
        codigo_repetido = db.session.execute(text("""
            SELECT 1 FROM estudianteinvestigador
            WHERE codigo_estudiantil = :codigo
        """), {"codigo": documento}).first()

        if codigo_repetido:
            return jsonify({
                "mensaje": "Ya existe un estudiante con este documento."
            }), 409

    try:
        _asegurar_administrador()

        nuevo = db.session.execute(text("""
            INSERT INTO usuario
                (nombre_institucional, correo_institucional, contrasena_hash,
                 fecha_nacimiento, rol, estado, fecha_registro)
            VALUES
                (:nombre, :correo, :clave, :nacimiento, :rol, 'ACTIVO', NOW())
        """), {
            "nombre": solicitud["nombre_completo"],
            "correo": solicitud["correo_institucional"],
            "clave": solicitud["contrasena_hash"],
            "nacimiento": solicitud["fecha_nacimiento"],
            "rol": rol
        })

        id_usuario = nuevo.lastrowid

        if rol == "ESTUDIANTE":
            db.session.execute(text("""
                INSERT INTO estudianteinvestigador
                    (id_usuario, codigo_estudiantil, id_programa,
                     semestre, xp_total)
                VALUES
                    (:id, :codigo, :programa, 1, 0)
            """), {
                "id": id_usuario,
                "codigo": documento,
                "programa": solicitud["id_programa"]
            })
        else:
            db.session.execute(text("""
                INSERT INTO docentelider (id_usuario) VALUES (:id)
            """), {"id": id_usuario})

        db.session.execute(text("""
            UPDATE solicitudregistro
            SET estado = 'APROBADA',
                fecha_resolucion = NOW(),
                id_admin_revisor = :admin,
                id_usuario_generado = :nuevo
            WHERE id_solicitud = :id
        """), {
            "admin": session.get("id_usuario"),
            "nuevo": id_usuario,
            "id": id_solicitud
        })

        _registrar_historial(
            "APROBAR_REGISTRO", id_solicitud, "PENDIENTE", "APROBADA"
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud aprobada. La cuenta ya está activa."
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL APROBAR SOLICITUD:", repr(error))
        return jsonify({"mensaje": "No fue posible aprobar la solicitud."}), 500


def rechazar_solicitud_registro(id_solicitud):
    solicitud = _buscar_solicitud_registro(id_solicitud)

    if not solicitud:
        return jsonify({"mensaje": "La solicitud no existe."}), 404

    if solicitud["estado"] != "PENDIENTE":
        return jsonify({"mensaje": "Esta solicitud ya fue resuelta."}), 409

    try:
        _asegurar_administrador()

        db.session.execute(text("""
            UPDATE solicitudregistro
            SET estado = 'RECHAZADA',
                fecha_resolucion = NOW(),
                id_admin_revisor = :admin
            WHERE id_solicitud = :id
        """), {"admin": session.get("id_usuario"), "id": id_solicitud})

        _registrar_historial(
            "RECHAZAR_REGISTRO", id_solicitud, "PENDIENTE", "RECHAZADA"
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud rechazada. La cuenta no fue creada."
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL RECHAZAR SOLICITUD:", repr(error))
        return jsonify({"mensaje": "No fue posible rechazar la solicitud."}), 500

# ==========================================
# CONVOCATORIAS DEL DOCENTE LIDER
# ==========================================

def obtener_convocatorias():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify({
            "convocatorias": [],
            "inscripciones": 0
        })

    filas = db.session.execute(text("""
        SELECT
            c.id_convocatoria,
            c.titulo,
            c.descripcion,
            c.fecha_inicio,
            c.fecha_cierre,
            c.modalidad,
            EXISTS (
                SELECT 1
                FROM inscripcionconvocatoria i
                WHERE i.id_convocatoria = c.id_convocatoria
                  AND i.id_semillero = :semillero
            ) AS inscrito
        FROM convocatoria c
        WHERE c.estado = 'ACTIVA'
          AND c.modalidad IN ('semillero', 'ambas')
          AND c.fecha_cierre >= CURDATE()
        ORDER BY c.fecha_cierre ASC, c.id_convocatoria DESC
    """), {"semillero": id_semillero}).mappings().all()

    inscripciones = db.session.execute(text("""
        SELECT COUNT(*)
        FROM inscripcionconvocatoria
        WHERE id_semillero = :semillero
    """), {"semillero": id_semillero}).scalar()

    return jsonify({
        "inscripciones": inscripciones,
        "convocatorias": [{
            "id": f["id_convocatoria"],
            "titulo": f["titulo"],
            "descripcion": f["descripcion"] or "",
            "inicio": f["fecha_inicio"].strftime("%d/%m/%Y"),
            "cierre": f["fecha_cierre"].strftime("%d/%m/%Y"),
            "modalidad": f["modalidad"],
            "inscrito": bool(f["inscrito"]),
        } for f in filas],
    })


# ==========================================
# EVENTOS DEL DOCENTE LIDER
# ==========================================

def obtener_eventos():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify({
            "eventos": [],
            "participaciones": 0
        })

    filas = db.session.execute(text("""
        SELECT
            e.id_evento,
            e.nombre,
            e.descripcion,
            e.fecha,
            e.lugar,
            e.modalidad,
            (
                SELECT COUNT(*)
                FROM participacionevento p
                WHERE p.id_evento = e.id_evento
                  AND p.id_semillero = :semillero
            ) AS participantes
        FROM evento e
        WHERE e.modalidad IN ('semillero', 'ambas')
        ORDER BY e.fecha ASC
    """), {"semillero": id_semillero}).mappings().all()

    participaciones = db.session.execute(text("""
        SELECT COUNT(*)
        FROM participacionevento
        WHERE id_semillero = :semillero
    """), {"semillero": id_semillero}).scalar()

    ahora = datetime.now()

    return jsonify({
        "participaciones": participaciones,
        "eventos": [{
            "id": f["id_evento"],
            "nombre": f["nombre"],
            "descripcion": f["descripcion"] or "",
            "fecha": f["fecha"].strftime("%d/%m/%Y %H:%M"),
            "lugar": f["lugar"] or "Por definir",
            "modalidad": f["modalidad"],
            "participantes": f["participantes"],
            "finalizado": f["fecha"] < ahora,
        } for f in filas],
    })

# ==========================================
# LOGROS DEL SEMILLERO
# ==========================================

def obtener_logros():
    id_semillero = _obtener_semillero_del_docente()

    if not id_semillero:
        return jsonify([])

    filas = db.session.execute(text("""
        SELECT
            l.id_logro,
            l.titulo,
            l.descripcion,
            l.estado,
            l.fecha_registro,
            l.porcentaje_calidad,
            u.nombre_institucional AS estudiante,
            tl.nombre AS tipo
        FROM logro l
        INNER JOIN membresiasemillero m
            ON m.id_estudiante = l.id_estudiante
           AND m.id_semillero = :semillero
           AND m.fecha_salida IS NULL
        INNER JOIN usuario u
            ON u.id_usuario = l.id_estudiante
        LEFT JOIN tipologro tl
            ON tl.id_tipo_logro = l.id_tipo_logro
        ORDER BY l.fecha_registro DESC
    """), {"semillero": id_semillero}).mappings().all()

    return jsonify([{
        "id": f["id_logro"],
        "estudiante": f["estudiante"],
        "titulo": f["titulo"] or f["tipo"] or "Logro",
        "descripcion": f["descripcion"] or "",
        "tipo": f["tipo"] or "—",
        "fecha": f["fecha_registro"].strftime("%d/%m/%Y"),
        "estado": f["estado"],
        "calidad": f["porcentaje_calidad"],
    } for f in filas])


def obtener_publicaciones():
    yo = session.get("id_usuario")

    filas = db.session.execute(text("""
        SELECT
            p.id_publicacion,
            p.id_usuario,
            p.contenido,
            p.tipo_publicacion,
            p.vistas,
            p.fecha_publicacion,
            u.nombre_institucional AS autor,
            s.nombre AS semillero,
            (
                SELECT COUNT(*)
                FROM comentario c
                WHERE c.id_publicacion = p.id_publicacion
            ) AS comentarios,
            (
                SELECT COUNT(*)
                FROM reaccion r
                WHERE r.id_publicacion = p.id_publicacion
            ) AS reacciones,
            EXISTS (
                SELECT 1
                FROM reaccion r2
                WHERE r2.id_publicacion = p.id_publicacion
                  AND r2.id_usuario = :yo
            ) AS yo_reaccione
        FROM publicacion p
        INNER JOIN usuario u
            ON u.id_usuario = p.id_usuario
        LEFT JOIN semillero s
            ON s.id_semillero = p.id_semillero
        ORDER BY p.fecha_publicacion DESC, p.id_publicacion DESC
        LIMIT 50
    """), {"yo": yo}).mappings().all()

    total = db.session.execute(text(
        "SELECT COUNT(*) FROM publicacion"
    )).scalar()

    academicas = db.session.execute(text(
        "SELECT COUNT(*) FROM publicacion WHERE tipo_publicacion = 'ACADEMICA'"
    )).scalar()

    return jsonify({
        "total": total,
        "academicas": academicas,
        "publicaciones": [{
            "id": f["id_publicacion"],
            "autor": f["autor"],
            "semillero": f["semillero"] or "",
            "contenido": f["contenido"],
            "academica": f["tipo_publicacion"] == "ACADEMICA",
            "vistas": f["vistas"],
            "fecha": f["fecha_publicacion"].strftime("%d/%m/%Y %H:%M"),
            "propia": f["id_usuario"] == yo,
            "comentarios": f["comentarios"],
            "reacciones": f["reacciones"],
            "yo_reaccione": bool(f["yo_reaccione"]),
        } for f in filas],
    })

def crear_publicacion():
    datos = request.get_json(silent=True) or {}
    contenido = (datos.get("contenido") or "").strip()
    academica = bool(datos.get("academica"))

    if not contenido:
        return jsonify({"mensaje": "Escribe algo para publicar."}), 400

    if len(contenido) > 3000:
        return jsonify({
            "mensaje": "La publicación no puede pasar de 3000 caracteres."
        }), 400

    try:
        db.session.execute(text("""
            INSERT INTO publicacion
                (id_usuario, id_semillero, contenido, tipo_publicacion,
                 vistas, fecha_publicacion, fecha_actualizacion)
            VALUES
                (:usuario, :semillero, :contenido, :tipo,
                 0, NOW(), NOW())
        """), {
            "usuario": session.get("id_usuario"),
            "semillero": _obtener_semillero_del_docente(),
            "contenido": contenido,
            "tipo": "ACADEMICA" if academica else "GENERAL",
        })

        db.session.commit()

        return jsonify({"mensaje": "Publicación creada."}), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR CREAR PUBLICACION:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar la publicación."
        }), 500

def reaccionar_publicacion(id_publicacion):
    yo = session.get("id_usuario")

    existe = db.session.execute(text(
        "SELECT 1 FROM publicacion WHERE id_publicacion = :id"
    ), {"id": id_publicacion}).first()

    if not existe:
        return jsonify({"mensaje": "La publicación no existe."}), 404

    try:
        ya_reacciono = db.session.execute(text("""
            SELECT 1
            FROM reaccion
            WHERE id_publicacion = :pub AND id_usuario = :yo
        """), {"pub": id_publicacion, "yo": yo}).first()

        if ya_reacciono:
            db.session.execute(text("""
                DELETE FROM reaccion
                WHERE id_publicacion = :pub AND id_usuario = :yo
            """), {"pub": id_publicacion, "yo": yo})
        else:
            db.session.execute(text("""
                INSERT INTO reaccion (id_publicacion, id_usuario, fecha)
                VALUES (:pub, :yo, NOW())
            """), {"pub": id_publicacion, "yo": yo})

        db.session.commit()

        total = db.session.execute(text("""
            SELECT COUNT(*) FROM reaccion WHERE id_publicacion = :pub
        """), {"pub": id_publicacion}).scalar()

        return jsonify({
            "reaccionado": not ya_reacciono,
            "total": total,
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR REACCION:", repr(error))
        return jsonify({
            "mensaje": "No fue posible registrar la reacción."
        }), 500

def obtener_comentarios(id_publicacion):
    filas = db.session.execute(text("""
        SELECT
            c.id_comentario,
            c.contenido,
            c.fecha,
            u.nombre_institucional AS autor
        FROM comentario c
        INNER JOIN usuario u
            ON u.id_usuario = c.id_usuario
        WHERE c.id_publicacion = :id
        ORDER BY c.fecha ASC, c.id_comentario ASC
    """), {"id": id_publicacion}).mappings().all()

    return jsonify([{
        "id": f["id_comentario"],
        "autor": f["autor"],
        "contenido": f["contenido"],
        "fecha": f["fecha"].strftime("%d/%m/%Y %H:%M"),
    } for f in filas])

def crear_comentario(id_publicacion):
    datos = request.get_json(silent=True) or {}
    contenido = (datos.get("contenido") or "").strip()

    if not contenido:
        return jsonify({"mensaje": "Escribe un comentario."}), 400

    if len(contenido) > 1000:
        return jsonify({
            "mensaje": "El comentario no puede pasar de 1000 caracteres."
        }), 400

    existe = db.session.execute(text(
        "SELECT 1 FROM publicacion WHERE id_publicacion = :id"
    ), {"id": id_publicacion}).first()

    if not existe:
        return jsonify({"mensaje": "La publicación no existe."}), 404

    try:
        db.session.execute(text("""
            INSERT INTO comentario
                (id_publicacion, id_usuario, contenido,
                 fecha, fecha_actualizacion)
            VALUES
                (:publicacion, :usuario, :contenido, NOW(), NOW())
        """), {
            "publicacion": id_publicacion,
            "usuario": session.get("id_usuario"),
            "contenido": contenido,
        })

        db.session.commit()

        return jsonify({"mensaje": "Comentario publicado."}), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR CREAR COMENTARIO:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar el comentario."
        }), 500

def obtener_ranking():
    id_semillero = _obtener_semillero_del_docente()

    estudiantes = db.session.execute(text("""
        SELECT
            RANK() OVER (ORDER BY e.xp_total DESC) AS posicion,
            u.nombre_institucional AS nombre,
            e.xp_total,
            n.nombre AS nivel,
            n.estrellas,
            (
                SELECT COUNT(*)
                FROM insigniaotorgada io
                WHERE io.id_usuario = e.id_usuario
            ) AS insignias
        FROM estudianteinvestigador e
        INNER JOIN usuario u
            ON u.id_usuario = e.id_usuario
        LEFT JOIN nivel n
            ON n.id_nivel = e.id_nivel_actual
        ORDER BY posicion, u.nombre_institucional
        LIMIT 10
    """)).mappings().all()

    semilleros = db.session.execute(text("""
        SELECT
            RANK() OVER (ORDER BY s.xp_total DESC) AS posicion,
            s.id_semillero,
            s.nombre,
            s.xp_total,
            n.nombre AS nivel,
            n.estrellas,
            (
                SELECT COUNT(*)
                FROM insigniaotorgada io
                WHERE io.id_semillero = s.id_semillero
            ) AS insignias
        FROM semillero s
        LEFT JOIN nivel n
            ON n.id_nivel = s.id_nivel_actual
        WHERE s.estado = 'ACTIVO'
        ORDER BY posicion, s.nombre
    """)).mappings().all()

    def fila(f):
        return {
            "posicion": f["posicion"],
            "nombre": f["nombre"],
            "xp": f["xp_total"],
            "nivel": f["nivel"] or "Sin nivel",
            "estrellas": f["estrellas"] or 0,
            "insignias": f["insignias"],
        }

    mio = next(
        (s for s in semilleros if s["id_semillero"] == id_semillero),
        None
    )

    return jsonify({
        "estudiantes": [fila(f) for f in estudiantes],
        "semilleros": [fila(f) for f in semilleros[:10]],
        "mi_posicion": mio["posicion"] if mio else None,
        "mi_xp": mio["xp_total"] if mio else 0,
    })


from flask import render_template, jsonify, request
from sqlalchemy import text
from app.extensions import db
import secrets
from datetime import datetime


def mostrar_panel():
    return render_template("admin/index.html")


def mostrar_usuarios():
    return render_template("admin/usuarios.html")


def mostrar_facultades():
    facultades = db.session.execute(text("""
        SELECT
            f.id_facultad,
            f.nombre,
            p.id_programa,
            p.nombre AS programa,
            s.id_semillero,
            s.nombre AS semillero
        FROM facultad f
        LEFT JOIN programa p
            ON p.id_facultad = f.id_facultad
        LEFT JOIN semillero s
            ON s.id_facultad = f.id_facultad
        ORDER BY f.nombre, p.nombre, s.nombre
    """)).mappings().all()

    resultado = {}

    for fila in facultades:
        id_facultad = fila["id_facultad"]

        if id_facultad not in resultado:
            resultado[id_facultad] = {
                "id_facultad": id_facultad,
                "nombre": fila["nombre"],
                "programas": {},
                "semilleros": {}
            }

        if fila["id_programa"]:
            resultado[id_facultad]["programas"][fila["id_programa"]] = fila["programa"]

        if fila["id_semillero"]:
            resultado[id_facultad]["semilleros"][fila["id_semillero"]] = fila["semillero"]

    facultades = []

    for facultad in resultado.values():
        facultad["programas"] = list(facultad["programas"].values())
        facultad["semilleros"] = list(facultad["semilleros"].values())
        facultades.append(facultad)

    return render_template(
        "admin/facultades.html",
        facultades=facultades
    )



def mostrar_semilleros():
    semilleros = db.session.execute(text("""
        SELECT
            s.id_semillero,
            s.nombre,
            s.descripcion,
            s.linea_investigacion,
            s.estado,
            s.cupo_maximo,
            s.fecha_creacion,
            f.nombre AS facultad,

            COALESCE((
                SELECT GROUP_CONCAT(DISTINCT pr.nombre
                    ORDER BY pr.nombre SEPARATOR ', ')
                FROM membresiasemillero m
                INNER JOIN estudianteinvestigador ei
                    ON ei.id_usuario = m.id_estudiante
                INNER JOIN programa pr
                    ON pr.id_programa = ei.id_programa
                WHERE m.id_semillero = s.id_semillero
                AND m.fecha_salida IS NULL
            ), 'Sin programa asignado') AS programa,

            (
                SELECT COUNT(*)
                FROM proyecto p
                WHERE p.id_semillero = s.id_semillero
            ) AS total_proyectos,

            (
                SELECT COUNT(*)
                FROM membresiasemillero m
                WHERE m.id_semillero = s.id_semillero
                AND m.fecha_salida IS NULL
            ) AS total_integrantes,

            (
                SELECT u.nombre_institucional
                FROM docentelider dl
                INNER JOIN usuario u
                    ON u.id_usuario = dl.id_usuario
                WHERE dl.id_semillero_liderado = s.id_semillero
            ) AS docente_lider

        FROM semillero s
        INNER JOIN facultad f
            ON f.id_facultad = s.id_facultad
        ORDER BY f.nombre, s.nombre
    """)).mappings().all()

    distribucion = db.session.execute(text("""
        SELECT
            f.nombre,
            COUNT(s.id_semillero) AS total
        FROM facultad f
        LEFT JOIN semillero s
            ON s.id_facultad = f.id_facultad
        GROUP BY f.id_facultad, f.nombre
        ORDER BY f.nombre
    """)).mappings().all()

    total_semilleros = len(semilleros)

    total_proyectos = sum(
        semillero["total_proyectos"] for semillero in semilleros
    )

    return render_template(
        "admin/semilleros.html",
        semilleros=semilleros,
        distribucion=distribucion,
        total_semilleros=total_semilleros,
        total_proyectos=total_proyectos
    )



def mostrar_convocatorias():
    convocatorias = db.session.execute(text("""
        SELECT
            id_convocatoria,
            titulo,
            descripcion,
            fecha_inicio,
            fecha_cierre,
            modalidad,
            estado
        FROM convocatoria
        ORDER BY fecha_inicio DESC
    """)).mappings().all()

    return render_template(
        "admin/convocatorias.html",
        convocatorias=convocatorias
    )



def mostrar_publicaciones():
    return render_template("admin/publicaciones.html")


def mostrar_logros():
    return render_template("admin/logros.html")


def mostrar_ranking():
    return render_template("admin/ranking.html")


def mostrar_reportes():
    return render_template("admin/reportes.html")



def mostrar_solicitudes():
    solicitudes = db.session.execute(text("""
        SELECT
            sr.id_solicitud,
            sr.nombre_completo,
            sr.correo_institucional,
            sr.documento,
            sr.rol_solicitado,
            sr.estado,
            sr.fecha_solicitud,
            f.nombre AS facultad,
            p.nombre AS programa
        FROM solicitudregistro sr
        LEFT JOIN facultad f
            ON f.id_facultad = sr.id_facultad
        LEFT JOIN programa p
            ON p.id_programa = sr.id_programa
        WHERE sr.estado = 'PENDIENTE'
        ORDER BY sr.fecha_solicitud DESC
    """)).mappings().all()

    return render_template(
        "admin/solicitudes.html",
        solicitudes=solicitudes
    )


def aprobar_solicitud_registro(id_solicitud):
    try:
        # Buscar y bloquear la solicitud
        solicitud = db.session.execute(text("""
            SELECT *
            FROM solicitudregistro
            WHERE id_solicitud = :id
            FOR UPDATE
        """), {"id": id_solicitud}).mappings().first()

        if not solicitud:
            db.session.rollback()
            return jsonify({
                "mensaje": "La solicitud no existe."
            }), 404

        if solicitud["estado"] != "PENDIENTE":
            db.session.rollback()
            return jsonify({
                "mensaje": "Esta solicitud ya fue procesada."
            }), 400

        rol = solicitud["rol_solicitado"]

        if rol not in ["ESTUDIANTE", "DOCENTE", "DOCENTE_LIDER"]:
            db.session.rollback()
            return jsonify({
                "mensaje": "El rol de la solicitud no es válido."
            }), 400

        if not solicitud["contrasena_hash"]:
            db.session.rollback()
            return jsonify({
                "mensaje": "La solicitud no tiene una contraseña registrada."
            }), 400

        if rol == "ESTUDIANTE" and not solicitud["id_programa"]:
            db.session.rollback()
            return jsonify({
                "mensaje": "La solicitud no tiene un programa académico."
            }), 400

        # Verificar que el correo no exista
        usuario_existente = db.session.execute(text("""
            SELECT id_usuario
            FROM usuario
            WHERE correo_institucional = :correo
        """), {
            "correo": solicitud["correo_institucional"]
        }).first()

        if usuario_existente:
            db.session.rollback()
            return jsonify({
                "mensaje": "Ya existe una cuenta con este correo."
            }), 409

        # Crear usuario principal
        resultado = db.session.execute(text("""
            INSERT INTO usuario (
                nombre_institucional,
                correo_institucional,
                contrasena_hash,
                fecha_nacimiento,
                documento,
                telefono,
                rol,
                estado,
                fecha_registro,
                intentos_fallidos
            )
            VALUES (
                :nombre,
                :correo,
                :contrasena,
                :fecha_nacimiento,
                :documento,
                :telefono,
                :rol,
                'ACTIVO',
                :fecha_registro,
                0
            )
        """), {
            "nombre": solicitud["nombre_completo"],
            "correo": solicitud["correo_institucional"],
            "contrasena": solicitud["contrasena_hash"],
            "fecha_nacimiento": solicitud["fecha_nacimiento"],
            "documento": solicitud["documento"],
            "telefono": solicitud["telefono"],
            "rol": rol,
            "fecha_registro": datetime.now()
        })

        id_usuario = resultado.lastrowid

        # Generar código único de cuatro dígitos
        codigo = None

        for intento in range(9000):
            candidato = str(secrets.randbelow(9000) + 1000)

            existe = db.session.execute(text("""
                SELECT
                    EXISTS (
                        SELECT 1 FROM estudianteinvestigador
                        WHERE codigo_estudiantil = :codigo
                    )
                    OR EXISTS (
                        SELECT 1 FROM docente
                        WHERE codigo_docente = :codigo
                    )
                    OR EXISTS (
                        SELECT 1 FROM docentelider
                        WHERE codigo_docente_lider = :codigo
                    ) AS existe
            """), {"codigo": candidato}).scalar()

            if not existe:
                codigo = candidato
                break

        if codigo is None:
            raise Exception("No hay códigos de cuatro dígitos disponibles.")

        # Crear perfil según el rol
        if rol == "ESTUDIANTE":

            db.session.execute(text("""
                INSERT INTO estudianteinvestigador (
                    id_usuario,
                    codigo_estudiantil,
                    id_programa,
                    semestre,
                    id_semillero,
                    xp_total,
                    id_nivel_actual,
                    fecha_actualizacion
                )
                VALUES (
                    :id_usuario,
                    :codigo,
                    :id_programa,
                    1,
                    NULL,
                    0,
                    NULL,
                    :fecha
                )
            """), {
                "id_usuario": id_usuario,
                "codigo": codigo,
                "id_programa": solicitud["id_programa"],
                "fecha": datetime.now()
            })

        elif rol == "DOCENTE":

            db.session.execute(text("""
                INSERT INTO docente (
                    id_usuario,
                    codigo_docente,
                    fecha_actualizacion
                )
                VALUES (
                    :id_usuario,
                    :codigo,
                    :fecha
                )
            """), {
                "id_usuario": id_usuario,
                "codigo": codigo,
                "fecha": datetime.now()
            })

        elif rol == "DOCENTE_LIDER":

            db.session.execute(text("""
                INSERT INTO docentelider (
                    id_usuario,
                    codigo_docente_lider,
                    id_semillero_liderado
                )
                VALUES (
                    :id_usuario,
                    :codigo,
                    NULL
                )
            """), {
                "id_usuario": id_usuario,
                "codigo": codigo
            })

        # Actualizar solicitud
        db.session.execute(text("""
            UPDATE solicitudregistro
            SET
                estado = 'APROBADA',
                fecha_resolucion = :fecha,
                id_usuario_generado = :id_usuario
            WHERE id_solicitud = :id_solicitud
        """), {
            "fecha": datetime.now(),
            "id_usuario": id_usuario,
            "id_solicitud": id_solicitud
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud aprobada correctamente. Código asignado: " + codigo
        }), 200

    except Exception as error:
        db.session.rollback()
        print("ERROR AL APROBAR REGISTRO:", repr(error))

        return jsonify({
            "mensaje": "No fue posible aprobar la solicitud."
        }), 500



def mostrar_solicitudes_actualizacion():
    solicitudes = db.session.execute(text("""
        SELECT
            sa.id_solicitud_act,
            sa.id_usuario,
            sa.campo_modificado,
            sa.valor_anterior,
            sa.valor_nuevo,
            sa.descripcion_solicitud,
            sa.estado,
            sa.fecha_solicitud,
            u.nombre_institucional,
            u.correo_institucional
        FROM solicitudactualizacion sa
        INNER JOIN usuario u
            ON u.id_usuario = sa.id_usuario
        WHERE sa.estado = 'PENDIENTE'
        ORDER BY sa.fecha_solicitud DESC
    """)).mappings().all()

    return solicitudes

def aprobar_solicitud_actualizacion(id_solicitud):

    solicitud = db.session.execute(text("""
        SELECT *
        FROM solicitudactualizacion
        WHERE id_solicitud_act = :id
          AND estado = 'PENDIENTE'
        FOR UPDATE
    """), {"id": id_solicitud}).mappings().first()

    if not solicitud:
        return jsonify({
            "mensaje": "La solicitud no existe o ya fue revisada."
        }), 404

    campos_permitidos = { 
        "nombre_institucional",
        "correo_institucional",
        "fecha_nacimiento",
        "telefono",
        "foto_perfil"
    }

    campo = solicitud["campo_modificado"]

    if campo not in campos_permitidos:
        return jsonify({
            "mensaje": "El campo solicitado no está permitido."
        }), 400

    try:
        db.session.execute(text(f"""
            UPDATE usuario
            SET {campo} = :valor,
                fecha_actualizacion = NOW()
            WHERE id_usuario = :id_usuario
        """), {
            "valor": solicitud["valor_nuevo"],
            "id_usuario": solicitud["id_usuario"]
        })

        db.session.execute(text("""
            UPDATE solicitudactualizacion
            SET estado = 'APROBADA',
                fecha_resolucion = NOW()
            WHERE id_solicitud_act = :id
        """), {"id": id_solicitud})

        # Crear notificacion para el estudiante
        db.session.execute(text("""
            INSERT INTO notificacion (
                id_usuario,
                mensaje,
                tipo,
                estado,
                fecha
            )
            VALUES (
                :id_usuario,
                :mensaje,
                'ACTUALIZACION',
                0,
                NOW()
            )
        """), {
            "id_usuario": solicitud["id_usuario"],
            "mensaje": "Tu solicitud de actualización de perfil fue aprobada."
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud aprobada correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()
        print("Error al aprobar solicitud:", error)

        return jsonify({
            "mensaje": "No se pudo aprobar la solicitud."
        }), 500

def rechazar_solicitud_actualizacion(id_solicitud, motivo):

    try:
        solicitud = db.session.execute(text("""
            SELECT id_usuario
            FROM solicitudactualizacion
            WHERE id_solicitud_act = :id
              AND estado = 'PENDIENTE'
            FOR UPDATE
        """), {
            "id": id_solicitud
        }).mappings().first()

        if not solicitud:
            return jsonify({
                "mensaje": "La solicitud no existe o ya fue revisada."
            }), 404

        db.session.execute(text("""
            UPDATE solicitudactualizacion
            SET estado = 'RECHAZADA',
                motivo_rechazo = :motivo,
                fecha_resolucion = NOW()
            WHERE id_solicitud_act = :id
        """), {
            "motivo": motivo,
            "id": id_solicitud
        })

        # Crear notificacion para el estudiante
        db.session.execute(text("""
            INSERT INTO notificacion (
                id_usuario,
                mensaje,
                tipo,
                estado,
                fecha
            )
            VALUES (
                :id_usuario,
                :mensaje,
                'ACTUALIZACION',
                0,
                NOW()
            )
        """), {
            "id_usuario": solicitud["id_usuario"],
            "mensaje": "Tu solicitud de actualización de perfil fue rechazada. Motivo: " + motivo
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Solicitud rechazada correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()
        print("Error al rechazar solicitud:", error)

        return jsonify({
            "mensaje": "No se pudo rechazar la solicitud."
        }), 500
    

def rechazar_solicitud_registro(id_solicitud):

    datos = request.get_json(silent=True) or {}
    motivo = datos.get("motivo", "").strip()

    if not motivo:
        return jsonify({
            "mensaje": "Debes escribir el motivo del rechazo."
        }), 400

    try:
        solicitud = db.session.execute(text("""
            SELECT estado
            FROM solicitudregistro
            WHERE id_solicitud = :id
            FOR UPDATE
        """), {"id": id_solicitud}).fetchone()

        if not solicitud:
            db.session.rollback()
            return jsonify({
                "mensaje": "La solicitud no existe."
            }), 404

        if solicitud.estado != "PENDIENTE":
            db.session.rollback()
            return jsonify({
                "mensaje": "Esta solicitud ya fue procesada."
            }), 400

        db.session.execute(text("""
            UPDATE solicitudregistro
            SET estado = 'RECHAZADA',
                motivo_rechazo = :motivo,
                fecha_resolucion = :fecha
            WHERE id_solicitud = :id
        """), {
            "motivo": motivo,
            "fecha": datetime.now(),
            "id": id_solicitud
        })

        db.session.commit()

        return jsonify({
            "mensaje": "La solicitud fue rechazada correctamente."
        }), 200

    except Exception as error:
        db.session.rollback()
        print("Error al rechazar solicitud:", error)

        return jsonify({
            "mensaje": "Ocurrió un error al rechazar la solicitud."
        }), 500
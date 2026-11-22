
from flask import render_template, jsonify, session
from sqlalchemy import text
from app.extensions import db


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

    if rol not in ("ESTUDIANTE", "DOCENTE"):
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



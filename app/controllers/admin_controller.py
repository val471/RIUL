
from flask import render_template, jsonify, request, session
from sqlalchemy import text
from app.extensions import db
import secrets
from datetime import datetime
import json
from flask import send_file
from reportlab.pdfgen import canvas
from io import BytesIO
from openpyxl import Workbook
from decimal import Decimal

def _contar(sql):
    """Ejecuta un COUNT y devuelve 0 si la consulta falla."""
    try:
        return db.session.execute(text(sql)).scalar() or 0
    except Exception as error:
        db.session.rollback()
        print("ERROR RESUMEN ADMIN:", repr(error))
        return 0


def mostrar_panel():
    solicitudes = (
        _contar("SELECT COUNT(*) FROM solicitudregistro WHERE estado = 'PENDIENTE'")
        + _contar("SELECT COUNT(*) FROM solicitudactualizacion WHERE estado = 'PENDIENTE'")
        + _contar("SELECT COUNT(*) FROM solicitudliderazgo WHERE estado = 'PENDIENTE'")
    )

    resumen = {
        "usuarios_activos": _contar(
            "SELECT COUNT(*) FROM usuario WHERE estado = 'ACTIVO'"),
        "usuarios_mes": _contar(
            "SELECT COUNT(*) FROM usuario WHERE estado = 'ACTIVO' "
            "AND fecha_registro >= DATE_FORMAT(NOW(), '%Y-%m-01')"),
        "semilleros_total": _contar(
            "SELECT COUNT(*) FROM semillero"),
        "semilleros_activos": _contar(
            "SELECT COUNT(*) FROM semillero WHERE estado = 'ACTIVO'"),
        "solicitudes": solicitudes,
        "logros": _contar(
            "SELECT COUNT(*) FROM logro WHERE estado = 'PENDIENTE'"),
    }

    return render_template("admin/index.html", resumen=resumen)



def mostrar_usuarios():
    usuarios = db.session.execute(text("""
        SELECT
            u.id_usuario,
            u.nombre_institucional,
            u.correo_institucional,
            u.rol,
            u.estado,
            p.nombre AS programa
        FROM usuario u
        LEFT JOIN estudianteinvestigador e
            ON e.id_usuario = u.id_usuario
        LEFT JOIN programa p
            ON p.id_programa = e.id_programa
        ORDER BY u.nombre_institucional
    """)).mappings().all()

    return render_template("admin/usuarios.html", usuarios=usuarios)


def cambiar_estado_usuario(id_usuario):
    """Suspende o activa una cuenta (RF-04) y lo deja en el historial (RF-44)."""
    id_admin = session.get("id_usuario")
    datos = request.get_json(silent=True) or {}
    nuevo_estado = (datos.get("estado") or "").strip().upper()

    if nuevo_estado not in ("ACTIVO", "SUSPENDIDO"):
        return jsonify({"mensaje": "Estado no válido."}), 400

    if id_usuario == id_admin:
        return jsonify({
            "mensaje": "No puedes suspender tu propia cuenta."
        }), 400

    try:
        actual = db.session.execute(text("""
            SELECT estado FROM usuario WHERE id_usuario = :id
        """), {"id": id_usuario}).first()

        if not actual:
            return jsonify({"mensaje": "El usuario no existe."}), 404

        if nuevo_estado == "ACTIVO":
            # Al activar también se limpia cualquier bloqueo por intentos fallidos
            db.session.execute(text("""
                UPDATE usuario
                SET estado = :estado,
                    fecha_actualizacion = NOW(),
                    intentos_fallidos = 0,
                    bloqueado_hasta = NULL
                WHERE id_usuario = :id
            """), {"estado": nuevo_estado, "id": id_usuario})
        else:
            db.session.execute(text("""
                UPDATE usuario
                SET estado = :estado,
                    fecha_actualizacion = NOW()
                WHERE id_usuario = :id
            """), {"estado": nuevo_estado, "id": id_usuario})

        db.session.execute(text("""
            INSERT INTO historial
                (id_usuario, accion, tabla_afectada, id_registro,
                 valor_anterior, valor_nuevo, fecha)
            VALUES
                (:admin, :accion, 'usuario', :registro,
                 :anterior, :nuevo, NOW())
        """), {
            "admin": id_admin,
            "accion": ("ACTIVAR_USUARIO" if nuevo_estado == "ACTIVO"
                       else "SUSPENDER_USUARIO"),
            "registro": id_usuario,
            "anterior": actual[0],
            "nuevo": nuevo_estado,
        })

        db.session.commit()
        return jsonify({"mensaje": "Estado actualizado correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CAMBIAR ESTADO DE USUARIO:", repr(error))
        return jsonify({"mensaje": "No fue posible cambiar el estado."}), 500


def mostrar_facultades():
    facultades = db.session.execute(text("""
        SELECT id_facultad, nombre FROM facultad ORDER BY nombre
    """)).mappings().all()

    programas = db.session.execute(text("""
        SELECT
            p.id_programa,
            p.nombre,
            p.id_facultad,
            (SELECT COUNT(*)
               FROM estudianteinvestigador e
              WHERE e.id_programa = p.id_programa) AS estudiantes
        FROM programa p
        ORDER BY p.nombre
    """)).mappings().all()

    semilleros = db.session.execute(text("""
        SELECT nombre, id_facultad FROM semillero ORDER BY nombre
    """)).mappings().all()

    resultado = []
    for f in facultades:
        progs = [dict(p) for p in programas
                 if p["id_facultad"] == f["id_facultad"]]
        sems = [s["nombre"] for s in semilleros
                if s["id_facultad"] == f["id_facultad"]]
        resultado.append({
            "id_facultad": f["id_facultad"],
            "nombre": f["nombre"],
            "programas": progs,
            "semilleros": sems,
            "estudiantes": sum(p["estudiantes"] for p in progs),
        })

    return render_template("admin/facultades.html", facultades=resultado)


def _limpiar_nombre(datos):
    """Quita espacios repetidos del nombre recibido."""
    return " ".join((datos.get("nombre") or "").split())


def _registrar_historial(id_admin, accion, tabla, id_registro, anterior, nuevo):
    db.session.execute(text("""
        INSERT INTO historial
            (id_usuario, accion, tabla_afectada, id_registro,
             valor_anterior, valor_nuevo, fecha)
        VALUES
            (:admin, :accion, :tabla, :registro, :anterior, :nuevo, NOW())
    """), {
        "admin": id_admin, "accion": accion, "tabla": tabla,
        "registro": id_registro, "anterior": anterior, "nuevo": nuevo,
    })


def crear_facultad():
    nombre = _limpiar_nombre(request.get_json(silent=True) or {})

    if not nombre:
        return jsonify({"mensaje": "Escribe el nombre de la facultad."}), 400
    if len(nombre) > 100:
        return jsonify({"mensaje": "El nombre no puede superar 100 caracteres."}), 400

    try:
        existe = db.session.execute(text("""
            SELECT 1 FROM facultad WHERE LOWER(nombre) = LOWER(:n)
        """), {"n": nombre}).first()
        if existe:
            return jsonify({"mensaje": "Ya existe una facultad con ese nombre."}), 409

        nueva = db.session.execute(text(
            "INSERT INTO facultad (nombre) VALUES (:n)"), {"n": nombre})

        _registrar_historial(session.get("id_usuario"), "CREAR_FACULTAD",
                             "facultad", nueva.lastrowid, None, nombre)
        db.session.commit()
        return jsonify({"mensaje": "Facultad creada correctamente."}), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CREAR FACULTAD:", repr(error))
        return jsonify({"mensaje": "No fue posible crear la facultad."}), 500


def editar_facultad(id_facultad):
    nombre = _limpiar_nombre(request.get_json(silent=True) or {})

    if not nombre:
        return jsonify({"mensaje": "Escribe el nombre de la facultad."}), 400
    if len(nombre) > 100:
        return jsonify({"mensaje": "El nombre no puede superar 100 caracteres."}), 400

    try:
        actual = db.session.execute(text(
            "SELECT nombre FROM facultad WHERE id_facultad = :id"),
            {"id": id_facultad}).first()
        if not actual:
            return jsonify({"mensaje": "La facultad no existe."}), 404

        repetida = db.session.execute(text("""
            SELECT 1 FROM facultad
            WHERE LOWER(nombre) = LOWER(:n) AND id_facultad <> :id
        """), {"n": nombre, "id": id_facultad}).first()
        if repetida:
            return jsonify({"mensaje": "Ya existe una facultad con ese nombre."}), 409

        db.session.execute(text(
            "UPDATE facultad SET nombre = :n WHERE id_facultad = :id"),
            {"n": nombre, "id": id_facultad})

        _registrar_historial(session.get("id_usuario"), "EDITAR_FACULTAD",
                             "facultad", id_facultad, actual[0], nombre)
        db.session.commit()
        return jsonify({"mensaje": "Facultad actualizada correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL EDITAR FACULTAD:", repr(error))
        return jsonify({"mensaje": "No fue posible actualizar la facultad."}), 500


def crear_programa(id_facultad):
    nombre = _limpiar_nombre(request.get_json(silent=True) or {})

    if not nombre:
        return jsonify({"mensaje": "Escribe el nombre del programa."}), 400
    if len(nombre) > 100:
        return jsonify({"mensaje": "El nombre no puede superar 100 caracteres."}), 400

    try:
        facultad = db.session.execute(text(
            "SELECT nombre FROM facultad WHERE id_facultad = :id"),
            {"id": id_facultad}).first()
        if not facultad:
            return jsonify({"mensaje": "La facultad no existe."}), 404

        repetido = db.session.execute(text("""
            SELECT 1 FROM programa
            WHERE LOWER(nombre) = LOWER(:n) AND id_facultad = :f
        """), {"n": nombre, "f": id_facultad}).first()
        if repetido:
            return jsonify({"mensaje": "Esa facultad ya tiene un programa con ese nombre."}), 409

        nuevo = db.session.execute(text("""
            INSERT INTO programa (nombre, id_facultad) VALUES (:n, :f)
        """), {"n": nombre, "f": id_facultad})

        _registrar_historial(session.get("id_usuario"), "CREAR_PROGRAMA",
                             "programa", nuevo.lastrowid, None,
                             nombre + " (" + facultad[0] + ")")
        db.session.commit()
        return jsonify({"mensaje": "Programa creado correctamente."}), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CREAR PROGRAMA:", repr(error))
        return jsonify({"mensaje": "No fue posible crear el programa."}), 500


def usuarios_facultad(id_facultad):
    """Estudiantes (por programa) y docentes líderes (por semillero) de una facultad."""
    try:
        filas = db.session.execute(text("""
            SELECT u.id_usuario, u.nombre_institucional AS nombre,
                   u.correo_institucional AS correo, 'ESTUDIANTE' AS rol,
                   p.nombre AS detalle, u.estado
            FROM estudianteinvestigador e
            JOIN usuario u ON u.id_usuario = e.id_usuario
            JOIN programa p ON p.id_programa = e.id_programa
            WHERE p.id_facultad = :f

            UNION ALL

            SELECT u.id_usuario, u.nombre_institucional,
                   u.correo_institucional, 'DOCENTE_LIDER',
                   CONCAT('Semillero: ', s.nombre), u.estado
            FROM docentelider d
            JOIN usuario u ON u.id_usuario = d.id_usuario
            JOIN semillero s ON s.id_semillero = d.id_semillero_liderado
            WHERE s.id_facultad = :f

            ORDER BY rol, nombre
        """), {"f": id_facultad}).mappings().all()

        return jsonify({"usuarios": [dict(f) for f in filas]})

    except Exception as error:
        print("ERROR USUARIOS DE FACULTAD:", repr(error))
        return jsonify({"mensaje": "No fue posible cargar los usuarios."}), 500

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

    facultades = db.session.execute(text("""
        SELECT id_facultad, nombre FROM facultad ORDER BY nombre
    """)).mappings().all()

    return render_template(
        "admin/semilleros.html",
        semilleros=semilleros,
        distribucion=distribucion,
        total_semilleros=total_semilleros,
        total_proyectos=total_proyectos,
        facultades=facultades
    )


def asignar_docente_lider(id_semillero):
    datos = request.get_json(silent=True) or {}
    id_usuario = datos.get("id_usuario")

    try:
        # Verificar que el semillero exista
        semillero = db.session.execute(text("""
            SELECT id_semillero, nombre
            FROM semillero
            WHERE id_semillero = :id
            FOR UPDATE
        """), {"id": id_semillero}).mappings().first()

        if not semillero:
            return jsonify({
                "mensaje": "El semillero no existe."
            }), 404

        # Consultar el docente que actualmente lo dirige
        actual = db.session.execute(text("""
            SELECT id_usuario
            FROM docentelider
            WHERE id_semillero_liderado = :id
        """), {"id": id_semillero}).first()

        id_anterior = actual[0] if actual else None

        # Si se envía vacío, quitar la asignación
        if id_usuario in (None, ""):
            if id_anterior is not None:
                db.session.execute(text("""
                    UPDATE docentelider
                    SET id_semillero_liderado = NULL
                    WHERE id_usuario = :id
                """), {"id": id_anterior})

            db.session.commit()

            return jsonify({
                "mensaje": "Docente líder desasignado correctamente."
            })

        try:
            id_usuario = int(id_usuario)
        except (TypeError, ValueError):
            return jsonify({
                "mensaje": "El docente seleccionado no es válido."
            }), 400

        # Verificar que sea un docente líder registrado
        docente = db.session.execute(text("""
            SELECT id_usuario
            FROM docentelider
            WHERE id_usuario = :id
            FOR UPDATE
        """), {"id": id_usuario}).first()

        if not docente:
            return jsonify({
                "mensaje": "El usuario seleccionado no es docente líder."
            }), 404

        # Evitar que el docente dirija otro semillero
        otra_asignacion = db.session.execute(text("""
            SELECT id_semillero_liderado
            FROM docentelider
            WHERE id_usuario = :id
        """), {"id": id_usuario}).scalar()

        if otra_asignacion is not None and otra_asignacion != id_semillero:
            return jsonify({
                "mensaje": "Este docente líder ya tiene otro semillero asignado."
            }), 409

        # Liberar al docente anterior
        if id_anterior is not None and id_anterior != id_usuario:
            db.session.execute(text("""
                UPDATE docentelider
                SET id_semillero_liderado = NULL
                WHERE id_usuario = :id
            """), {"id": id_anterior})

        # Asignar el nuevo docente
        db.session.execute(text("""
            UPDATE docentelider
            SET id_semillero_liderado = :semillero
            WHERE id_usuario = :usuario
        """), {
            "semillero": id_semillero,
            "usuario": id_usuario
        })

        _registrar_historial(
            session.get("id_usuario"),
            "ASIGNAR_DOCENTE_LIDER",
            "semillero",
            id_semillero,
            str(id_anterior) if id_anterior else "Sin asignar",
            str(id_usuario)
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Docente líder asignado correctamente."
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL ASIGNAR DOCENTE LIDER:", repr(error))

        return jsonify({
            "mensaje": "No fue posible asignar el docente líder."
        }), 500


def obtener_docentes_disponibles(id_semillero):
    try:
        docentes = db.session.execute(text("""
            SELECT
                u.id_usuario,
                u.nombre_institucional,
                dl.id_semillero_liderado
            FROM docentelider dl
            INNER JOIN usuario u
                ON u.id_usuario = dl.id_usuario
            WHERE u.rol = 'DOCENTE_LIDER'
              AND u.estado = 'ACTIVO'
              AND (
                  dl.id_semillero_liderado IS NULL
                  OR dl.id_semillero_liderado = :id_semillero
              )
            ORDER BY u.nombre_institucional
        """), {"id_semillero": id_semillero}).mappings().all()

        return jsonify({
            "docentes": [dict(d) for d in docentes]
        })

    except Exception as error:
        print("ERROR AL CONSULTAR DOCENTES DISPONIBLES:", repr(error))
        return jsonify({
            "mensaje": "No fue posible consultar los docentes líderes."
        }), 500


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
                    id_semillero_liderado,
                    id_programa
                )
                VALUES (
                    :id_usuario,
                    :codigo,
                    NULL,
                    :id_programa,
                )
            """), {
                "id_usuario": id_usuario,
                "codigo": codigo,
                "id_prgrama": solicitud.id_programa
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

def _guardar_notificacion_admin(mensaje):
    """Deja guardado en la tabla notificacion el aviso de lo que resolvió el admin."""
    db.session.execute(text("""
        INSERT INTO notificacion (id_usuario, mensaje, tipo, estado, fecha)
        VALUES (:id_usuario, :mensaje, 'RESUELTA', 1, NOW())
    """), {
        "id_usuario": session.get("id_usuario"),
        "mensaje": mensaje
    })


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

        nombre = db.session.execute(text(
            "SELECT nombre_institucional FROM usuario WHERE id_usuario = :id"
        ), {"id": solicitud["id_usuario"]}).scalar()

        _guardar_notificacion_admin(
            "Aprobaste la solicitud de " + str(nombre) +
            ": cambio de " + solicitud["campo_modificado"] + "."
        )

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
            SELECT id_usuario, campo_modificado
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

        nombre = db.session.execute(text(
            "SELECT nombre_institucional FROM usuario WHERE id_usuario = :id"
        ), {"id": solicitud["id_usuario"]}).scalar()

        _guardar_notificacion_admin(
            "Rechazaste la solicitud de " + str(nombre) +
            ": cambio de " + solicitud["campo_modificado"] +
            ". Motivo: " + motivo
        )

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

def _validar_datos_semillero(datos):
    """Limpia y valida lo que llega del formulario de semillero."""
    nombre = " ".join((datos.get("nombre") or "").split())
    linea = " ".join((datos.get("linea_investigacion") or "").split())
    descripcion = (datos.get("descripcion") or "").strip()

    try:
        id_facultad = int(datos.get("id_facultad"))
        cupo = int(datos.get("cupo_maximo"))
    except (TypeError, ValueError):
        return None, "Selecciona la facultad e indica un cupo válido."

    if not nombre:
        return None, "Escribe el nombre del semillero."
    if len(nombre) > 100:
        return None, "El nombre no puede superar 100 caracteres."
    if len(linea) > 100:
        return None, "La línea de investigación no puede superar 100 caracteres."
    if cupo < 1 or cupo > 500:
        return None, "El cupo debe estar entre 1 y 500."

    return {
        "nombre": nombre,
        "linea": linea,
        "descripcion": descripcion,
        "id_facultad": id_facultad,
        "cupo": cupo,
    }, None


def crear_semillero():
    datos, error = _validar_datos_semillero(request.get_json(silent=True) or {})
    if error:
        return jsonify({"mensaje": error}), 400

    try:
        if not db.session.execute(text(
                "SELECT 1 FROM facultad WHERE id_facultad = :f"),
                {"f": datos["id_facultad"]}).first():
            return jsonify({"mensaje": "La facultad seleccionada no existe."}), 400

        if db.session.execute(text(
                "SELECT 1 FROM semillero WHERE LOWER(nombre) = LOWER(:n)"),
                {"n": datos["nombre"]}).first():
            return jsonify({"mensaje": "Ya existe un semillero con ese nombre."}), 409

        nuevo = db.session.execute(text("""
            INSERT INTO semillero
                (nombre, descripcion, linea_investigacion, estado,
                 cupo_maximo, fecha_creacion, id_facultad, xp_total)
            VALUES
                (:nombre, :descripcion, :linea, 'ACTIVO',
                 :cupo, NOW(), :facultad, 0)
        """), {
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"] or None,
            "linea": datos["linea"] or None,
            "cupo": datos["cupo"],
            "facultad": datos["id_facultad"],
        })

        _registrar_historial(session.get("id_usuario"), "CREAR_SEMILLERO",
                             "semillero", nuevo.lastrowid, None, datos["nombre"])
        db.session.commit()
        return jsonify({"mensaje": "Semillero creado correctamente."}), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CREAR SEMILLERO:", repr(error))
        return jsonify({"mensaje": "No fue posible crear el semillero."}), 500


def detalle_semillero(id_semillero):
    try:
        s = db.session.execute(text("""
            SELECT
                s.id_semillero, s.nombre, s.descripcion,
                s.linea_investigacion, s.estado, s.cupo_maximo,
                s.xp_total, s.id_facultad, f.nombre AS facultad,
                (SELECT u.nombre_institucional
                   FROM docentelider dl
                   JOIN usuario u ON u.id_usuario = dl.id_usuario
                  WHERE dl.id_semillero_liderado = s.id_semillero) AS docente_lider
            FROM semillero s
            JOIN facultad f ON f.id_facultad = s.id_facultad
            WHERE s.id_semillero = :id
        """), {"id": id_semillero}).mappings().first()

        if not s:
            return jsonify({"mensaje": "El semillero no existe."}), 404

        integrantes = db.session.execute(text("""
            SELECT u.nombre_institucional AS nombre,
                   p.nombre AS programa,
                   m.fecha_ingreso
            FROM membresiasemillero m
            JOIN usuario u ON u.id_usuario = m.id_estudiante
            LEFT JOIN estudianteinvestigador e ON e.id_usuario = m.id_estudiante
            LEFT JOIN programa p ON p.id_programa = e.id_programa
            WHERE m.id_semillero = :id AND m.fecha_salida IS NULL
            ORDER BY u.nombre_institucional
        """), {"id": id_semillero}).mappings().all()

        proyectos = db.session.execute(text("""
            SELECT titulo, estado
            FROM proyecto
            WHERE id_semillero = :id
            ORDER BY fecha_inicio DESC
        """), {"id": id_semillero}).mappings().all()

        return jsonify({
            "semillero": dict(s),
            "integrantes": [{
                "nombre": i["nombre"],
                "programa": i["programa"],
                "ingreso": (i["fecha_ingreso"].strftime("%d/%m/%Y")
                            if i["fecha_ingreso"] else None),
            } for i in integrantes],
            "proyectos": [dict(p) for p in proyectos],
        })

    except Exception as error:
        print("ERROR DETALLE SEMILLERO:", repr(error))
        return jsonify({"mensaje": "No fue posible cargar el semillero."}), 500


def editar_semillero(id_semillero):
    datos, error = _validar_datos_semillero(request.get_json(silent=True) or {})
    if error:
        return jsonify({"mensaje": error}), 400

    try:
        actual = db.session.execute(text("""
            SELECT nombre, descripcion, linea_investigacion,
                   id_facultad, cupo_maximo
            FROM semillero WHERE id_semillero = :id
        """), {"id": id_semillero}).mappings().first()

        if not actual:
            return jsonify({"mensaje": "El semillero no existe."}), 404

        if not db.session.execute(text(
                "SELECT 1 FROM facultad WHERE id_facultad = :f"),
                {"f": datos["id_facultad"]}).first():
            return jsonify({"mensaje": "La facultad seleccionada no existe."}), 400

        if db.session.execute(text("""
                SELECT 1 FROM semillero
                WHERE LOWER(nombre) = LOWER(:n) AND id_semillero <> :id
        """), {"n": datos["nombre"], "id": id_semillero}).first():
            return jsonify({"mensaje": "Ya existe un semillero con ese nombre."}), 409

        activos = db.session.execute(text("""
            SELECT COUNT(*) FROM membresiasemillero
            WHERE id_semillero = :id AND fecha_salida IS NULL
        """), {"id": id_semillero}).scalar() or 0

        if datos["cupo"] < activos:
            return jsonify({
                "mensaje": "El cupo no puede ser menor que los "
                           + str(activos) + " integrantes actuales."
            }), 400

        db.session.execute(text("""
            UPDATE semillero
            SET nombre = :nombre,
                descripcion = :descripcion,
                linea_investigacion = :linea,
                id_facultad = :facultad,
                cupo_maximo = :cupo,
                fecha_actualizacion = NOW()
            WHERE id_semillero = :id
        """), {
            "nombre": datos["nombre"],
            "descripcion": datos["descripcion"] or None,
            "linea": datos["linea"] or None,
            "facultad": datos["id_facultad"],
            "cupo": datos["cupo"],
            "id": id_semillero,
        })

        cambios = []
        if actual["nombre"] != datos["nombre"]:
            cambios.append("nombre: " + datos["nombre"])
        if (actual["linea_investigacion"] or "") != datos["linea"]:
            cambios.append("línea de investigación")
        if actual["id_facultad"] != datos["id_facultad"]:
            cambios.append("facultad: " + str(datos["id_facultad"]))
        if actual["cupo_maximo"] != datos["cupo"]:
            cambios.append("cupo: " + str(datos["cupo"]))
        if (actual["descripcion"] or "").strip() != datos["descripcion"]:
            cambios.append("descripción")

        _registrar_historial(session.get("id_usuario"), "EDITAR_SEMILLERO",
                             "semillero", id_semillero, actual["nombre"],
                             "; ".join(cambios) or "Sin cambios")
        db.session.commit()
        return jsonify({"mensaje": "Semillero actualizado correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL EDITAR SEMILLERO:", repr(error))
        return jsonify({"mensaje": "No fue posible actualizar el semillero."}), 500


def cambiar_estado_semillero(id_semillero):
    """Da de baja o reactiva un semillero (RF-06)."""
    datos = request.get_json(silent=True) or {}
    nuevo = (datos.get("estado") or "").strip().upper()

    if nuevo not in ("ACTIVO", "INACTIVO"):
        return jsonify({"mensaje": "Estado no válido."}), 400

    try:
        actual = db.session.execute(text(
            "SELECT estado FROM semillero WHERE id_semillero = :id"),
            {"id": id_semillero}).first()

        if not actual:
            return jsonify({"mensaje": "El semillero no existe."}), 404

        db.session.execute(text("""
            UPDATE semillero
            SET estado = :estado, fecha_actualizacion = NOW()
            WHERE id_semillero = :id
        """), {"estado": nuevo, "id": id_semillero})

        _registrar_historial(
            session.get("id_usuario"),
            "REACTIVAR_SEMILLERO" if nuevo == "ACTIVO" else "DAR_BAJA_SEMILLERO",
            "semillero", id_semillero, actual[0], nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Estado actualizado correctamente."})

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CAMBIAR ESTADO DE SEMILLERO:", repr(error))
        return jsonify({"mensaje": "No fue posible cambiar el estado."}), 500
CONDICION_LOGROS_ADMIN = """
    (l.estado = 'EN_VALIDACION'
     OR (l.estado = 'PENDIENTE'
         AND NOT EXISTS (
             SELECT 1 FROM membresiasemillero mm
             WHERE mm.id_estudiante = l.id_estudiante
               AND mm.fecha_salida IS NULL)))
"""


def obtener_logros_validacion():
    filas = db.session.execute(text(f"""
        SELECT
            l.id_logro,
            l.titulo,
            l.descripcion,
            l.estado,
            l.fecha_registro,
            l.porcentaje_calidad,
            u.nombre_institucional AS estudiante,
            tl.nombre AS tipo,
            tl.xp_otorgado,
            s.nombre AS semillero
        FROM logro l
        INNER JOIN usuario u
            ON u.id_usuario = l.id_estudiante
        LEFT JOIN tipologro tl
            ON tl.id_tipo_logro = l.id_tipo_logro
        LEFT JOIN membresiasemillero m
            ON m.id_estudiante = l.id_estudiante
           AND m.fecha_salida IS NULL
        LEFT JOIN semillero s
            ON s.id_semillero = m.id_semillero
        WHERE {CONDICION_LOGROS_ADMIN}
        ORDER BY l.fecha_registro
    """)).mappings().all()

    respuesta = []

    for f in filas:
        base = f["xp_otorgado"] or 0
        calidad = f["porcentaje_calidad"] or 100

        respuesta.append({
            "id": f["id_logro"],
            "estudiante": f["estudiante"],
            "titulo": f["titulo"] or f["tipo"] or "Logro",
            "descripcion": f["descripcion"] or "",
            "tipo": f["tipo"] or "—",
            "semillero": f["semillero"] or "Sin semillero",
            "fecha": f["fecha_registro"].strftime("%d/%m/%Y"),
            "estado": f["estado"],
            "xp_base": base,
            "calidad": f["porcentaje_calidad"],
            "xp_final": (base * calidad) // 100,
        })

    return jsonify(respuesta)


def _buscar_logro_validable(id_logro):
    return db.session.execute(text(f"""
        SELECT
            l.id_logro,
            l.id_estudiante,
            l.id_tipo_logro,
            l.porcentaje_calidad,
            l.estado,
            tl.xp_otorgado,
            tl.limite_semanal
        FROM logro l
        LEFT JOIN tipologro tl
            ON tl.id_tipo_logro = l.id_tipo_logro
        WHERE l.id_logro = :id
          AND {CONDICION_LOGROS_ADMIN}
        FOR UPDATE
    """), {"id": id_logro}).mappings().first()


def aprobar_logro(id_logro):
    id_admin = session.get("id_usuario")

    try:
        logro = _buscar_logro_validable(id_logro)

        if not logro:
            db.session.rollback()
            return jsonify({
                "mensaje": "El logro no existe o ya fue resuelto."
            }), 409

        if logro["limite_semanal"]:
            aprobados = db.session.execute(text("""
                SELECT COUNT(*) FROM logro
                WHERE id_estudiante = :estudiante
                  AND id_tipo_logro = :tipo
                  AND estado = 'APROBADO'
                  AND YEARWEEK(fecha_validacion, 1) = YEARWEEK(NOW(), 1)
            """), {
                "estudiante": logro["id_estudiante"],
                "tipo": logro["id_tipo_logro"]
            }).scalar() or 0

            if aprobados >= logro["limite_semanal"]:
                db.session.rollback()
                return jsonify({
                    "mensaje": "El estudiante ya alcanzó el límite "
                               "semanal para este tipo de logro."
                }), 409

        base = logro["xp_otorgado"] or 0
        calidad = logro["porcentaje_calidad"] or 100
        xp = (base * calidad) // 100

        id_semillero = db.session.execute(text("""
            SELECT id_semillero FROM membresiasemillero
            WHERE id_estudiante = :id AND fecha_salida IS NULL
            LIMIT 1
        """), {"id": logro["id_estudiante"]}).scalar()

        db.session.execute(text("""
            INSERT IGNORE INTO administrador (id_usuario) VALUES (:id)
        """), {"id": id_admin})

        db.session.execute(text("""
            UPDATE logro
            SET estado = 'APROBADO',
                id_admin_validador = :admin,
                fecha_validacion = NOW()
            WHERE id_logro = :id
        """), {"admin": id_admin, "id": id_logro})

        db.session.execute(text("""
            UPDATE estudianteinvestigador
            SET xp_total = xp_total + :xp,
                fecha_actualizacion = NOW()
            WHERE id_usuario = :estudiante
        """), {"xp": xp, "estudiante": logro["id_estudiante"]})

        db.session.execute(text("""
            INSERT INTO historialxp
                (id_estudiante, id_semillero, id_logro, cantidad_xp, fecha)
            VALUES
                (:estudiante, :semillero, :logro, :xp, NOW())
        """), {
            "estudiante": logro["id_estudiante"],
            "semillero": id_semillero,
            "logro": id_logro,
            "xp": xp
        })

        _registrar_historial(
            id_admin, "APROBAR_LOGRO", "logro", id_logro,
            logro["estado"], "APROBADO (+" + str(xp) + " XP)"
        )

        db.session.commit()

        return jsonify({
            "mensaje": "Logro aprobado. Se acreditaron "
                       + str(xp) + " XP al estudiante."
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR APROBAR LOGRO:", repr(error))
        return jsonify({"mensaje": "No fue posible aprobar el logro."}), 500


def rechazar_logro(id_logro):
    id_admin = session.get("id_usuario")

    try:
        logro = _buscar_logro_validable(id_logro)

        if not logro:
            db.session.rollback()
            return jsonify({
                "mensaje": "El logro no existe o ya fue resuelto."
            }), 409

        db.session.execute(text("""
            INSERT IGNORE INTO administrador (id_usuario) VALUES (:id)
        """), {"id": id_admin})

        db.session.execute(text("""
            UPDATE logro
            SET estado = 'RECHAZADO',
                id_admin_validador = :admin,
                fecha_validacion = NOW()
            WHERE id_logro = :id
        """), {"admin": id_admin, "id": id_logro})

        _registrar_historial(
            id_admin, "RECHAZAR_LOGRO", "logro", id_logro,
            logro["estado"], "RECHAZADO"
        )

        db.session.commit()

        return jsonify({"mensaje": "Logro rechazado. No se otorgó XP."})

    except Exception as error:
        db.session.rollback()
        print("ERROR RECHAZAR LOGRO:", repr(error))
        return jsonify({"mensaje": "No fue posible rechazar el logro."}), 500

def obtener_ranking_admin():
    estudiantes = db.session.execute(text("""
        SELECT
            RANK() OVER (ORDER BY e.xp_total DESC) AS posicion,
            u.nombre_institucional AS nombre,
            e.xp_total,
            n.nombre AS nivel,
            n.estrellas,
            (
                SELECT COUNT(*) FROM insigniaotorgada io
                WHERE io.id_usuario = e.id_usuario
            ) AS insignias
        FROM estudianteinvestigador e
        INNER JOIN usuario u ON u.id_usuario = e.id_usuario
        LEFT JOIN nivel n ON n.id_nivel = e.id_nivel_actual
        ORDER BY posicion, u.nombre_institucional
        LIMIT 10
    """)).mappings().all()

    semilleros = db.session.execute(text("""
        SELECT
            RANK() OVER (ORDER BY s.xp_total DESC) AS posicion,
            s.nombre,
            s.xp_total,
            n.nombre AS nivel,
            n.estrellas,
            (
                SELECT COUNT(*) FROM insigniaotorgada io
                WHERE io.id_semillero = s.id_semillero
            ) AS insignias
        FROM semillero s
        LEFT JOIN nivel n ON n.id_nivel = s.id_nivel_actual
        WHERE s.estado = 'ACTIVO'
        ORDER BY posicion, s.nombre
        LIMIT 10
    """)).mappings().all()

    def fila(f):
        return {
            "posicion": f["posicion"],
            "nombre": f["nombre"],
            "xp": f["xp_total"] or 0,
            "nivel": f["nivel"] or "Sin nivel",
            "estrellas": f["estrellas"] or 0,
            "insignias": f["insignias"],
        }

    return jsonify({
        "estudiantes": [fila(f) for f in estudiantes],
        "semilleros": [fila(f) for f in semilleros],
    })

def obtener_datos_resumen_reportes():
    def uno(sql):
        return db.session.execute(text(sql)).scalar() or 0

    def filas(sql):
        return [
            dict(f)
            for f in db.session.execute(text(sql)).mappings().all()
        ]

    return {
        "usuarios": {
            "total": uno("SELECT COUNT(*) FROM usuario"),
            "activos": uno(
                "SELECT COUNT(*) FROM usuario WHERE estado='ACTIVO'"
            ),
            "por_rol": filas("""
                SELECT rol, COUNT(*) AS total
                FROM usuario
                GROUP BY rol
                ORDER BY total DESC
            """)
        },
        "semilleros": {
            "total": uno("SELECT COUNT(*) FROM semillero"),
            "activos": uno(
                "SELECT COUNT(*) FROM semillero WHERE estado='ACTIVO'"
            )
        },
        "proyectos_por_facultad": filas("""
            SELECT f.nombre AS facultad,
                   COUNT(p.id_proyecto) AS total
            FROM facultad f
            LEFT JOIN semillero s
                ON s.id_facultad = f.id_facultad
            LEFT JOIN proyecto p
                ON p.id_semillero = s.id_semillero
            GROUP BY f.id_facultad, f.nombre
            ORDER BY total DESC
        """),
        "logros": filas("""
            SELECT estado, COUNT(*) AS total
            FROM logro
            GROUP BY estado
        """),
        "xp_acreditado": uno("""
            SELECT COALESCE(SUM(cantidad_xp), 0)
            FROM historialxp
        """)
    }


def obtener_resumen_reportes():
    try:
        return jsonify(obtener_datos_resumen_reportes())

    except Exception as error:
        db.session.rollback()
        print("ERROR REPORTES:", repr(error))

        return jsonify({
            "mensaje": "No fue posible generar el reporte."
        }), 500

# Convertir valores Decimal para poder guardarlos como JSON
def convertir_valor_json(valor):
    if isinstance(valor, Decimal):
        if valor == valor.to_integral_value():
            return int(valor)
        return float(valor)

    raise TypeError(
        f"Tipo de dato no serializable: {type(valor).__name__}"
    )

def guardar_reporte():
    try:
        datos = obtener_datos_resumen_reportes()

        id_admin = session.get("id_usuario")

        if not id_admin:
            return jsonify({
                "mensaje": "Debes iniciar sesión como administrador."
            }), 401

        nombre = "Reporte general RIUL"
        periodo = datetime.now().strftime("%B %Y")

        resultado = db.session.execute(text("""
            INSERT INTO reportegenerado (
                id_admin,
                nombre_reporte,
                periodo,
                contenido,
                fecha_generacion
            )
            VALUES (
                :admin,
                :nombre,
                :periodo,
                :contenido,
                NOW()
            )
        """), {
            "admin": id_admin,
            "nombre": nombre,
            "periodo": periodo,
            "contenido": json.dumps(datos, ensure_ascii=False,  default=convertir_valor_json)
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Reporte guardado correctamente.",
            "id_reporte": resultado.lastrowid
        }), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR AL GUARDAR REPORTE:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar el reporte."
        }), 500

def listar_reportes():
    try:
        id_admin = session.get("id_usuario")

        if not id_admin:
            return jsonify({
                "mensaje": "Debes iniciar sesión como administrador."
            }), 401

        reportes = db.session.execute(text("""
            SELECT
                id_reporte,
                nombre_reporte,
                periodo,
                fecha_generacion
            FROM reportegenerado
            WHERE id_admin = :admin
            ORDER BY fecha_generacion DESC
        """), {
            "admin": id_admin
        }).mappings().all()

        return jsonify([
            {
                "id_reporte": r["id_reporte"],
                "nombre_reporte": r["nombre_reporte"],
                "periodo": r["periodo"],
                "formato": "PDF / Excel",
                "estado": "Disponible",
                "fecha_generacion": r["fecha_generacion"].strftime("%d/%m/%Y %H:%M")
            }
            for r in reportes
        ])

    except Exception as error:
        db.session.rollback()
        print("ERROR HISTORIAL REPORTES:", repr(error))

        return jsonify({
            "mensaje": "No fue posible consultar el historial."
        }), 500
def obtener_reporte(id_reporte):
    try:
        id_admin = session.get("id_usuario")

        if not id_admin:
            return jsonify({
                "mensaje": "Debes iniciar sesión como administrador."
            }), 401

        reporte = db.session.execute(text("""
            SELECT
                id_reporte,
                nombre_reporte,
                periodo,
                contenido,
                fecha_generacion
            FROM reportegenerado
            WHERE id_reporte = :id
              AND id_admin = :admin
        """), {
            "id": id_reporte,
            "admin": id_admin
        }).mappings().first()

        if not reporte:
            return jsonify({
                "mensaje": "No se encontró el reporte."
            }), 404

        contenido = reporte["contenido"]

        if isinstance(contenido, str):
            contenido = json.loads(contenido)

        return jsonify({
            "id_reporte": reporte["id_reporte"],
            "nombre_reporte": reporte["nombre_reporte"],
            "periodo": reporte["periodo"],
            "fecha_generacion": reporte["fecha_generacion"].strftime(
                "%d/%m/%Y %H:%M"
            ),
            "contenido": contenido
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR AL CONSULTAR REPORTE:", repr(error))

        return jsonify({
            "mensaje": "No fue posible abrir el reporte."
        }), 500
def descargar_reporte_pdf(id_reporte):
    try:
        id_admin = session.get("id_usuario")

        if not id_admin:
            return jsonify({"mensaje": "Sesión no válida."}), 401

        reporte = db.session.execute(text("""
            SELECT nombre_reporte, periodo, contenido
            FROM reportegenerado
            WHERE id_reporte = :id AND id_admin = :admin
        """), {
            "id": id_reporte,
            "admin": id_admin
        }).mappings().first()

        if not reporte:
            return jsonify({"mensaje": "Reporte no encontrado."}), 404

        datos = reporte["contenido"]

        if isinstance(datos, str):
            datos = json.loads(datos)

        archivo = BytesIO()
        pdf = canvas.Canvas(archivo, pagesize=(612, 792))

        ancho, alto = 612, 792
        y = alto - 50

        def escribir(texto):
            nonlocal y

            if y < 50:
                pdf.showPage()
                y = alto - 50

            pdf.drawString(50, y, str(texto)[:100])
            y -= 22

        escribir("REPORTE RIUL")
        escribir(reporte["nombre_reporte"])
        escribir("Periodo: " + str(reporte["periodo"]))
        escribir("")

        escribir("USUARIOS")
        escribir("Total: " + str(datos["usuarios"]["total"]))
        escribir("Activos: " + str(datos["usuarios"]["activos"]))

        for item in datos["usuarios"]["por_rol"]:
            escribir(str(item["rol"]) + ": " + str(item["total"]))

        escribir("")
        escribir("SEMILLEROS")
        escribir("Total: " + str(datos["semilleros"]["total"]))
        escribir("Activos: " + str(datos["semilleros"]["activos"]))

        escribir("")
        escribir("PROYECTOS POR FACULTAD")

        for item in datos["proyectos_por_facultad"]:
            escribir(str(item["facultad"]) + ": " + str(item["total"]))

        escribir("")
        escribir("LOGROS POR ESTADO")

        for item in datos["logros"]:
            escribir(str(item["estado"]) + ": " + str(item["total"]))

        escribir("")
        escribir("XP ACREDITADO: " + str(datos["xp_acreditado"]))

        pdf.save()
        archivo.seek(0)

        return send_file(
            archivo,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"reporte_RIUL_{id_reporte}.pdf"
        )

    except Exception as error:
        db.session.rollback()
        print("ERROR PDF:", repr(error))
        return jsonify({"mensaje": "No fue posible generar el PDF."}), 500

def descargar_reporte_excel(id_reporte):
    try:
        id_admin = session.get("id_usuario")

        if not id_admin:
            return jsonify({"mensaje": "Sesión no válida."}), 401

        reporte = db.session.execute(text("""
            SELECT nombre_reporte, periodo, contenido
            FROM reportegenerado
            WHERE id_reporte = :id AND id_admin = :admin
        """), {
            "id": id_reporte,
            "admin": id_admin
        }).mappings().first()

        if not reporte:
            return jsonify({"mensaje": "Reporte no encontrado."}), 404

        datos = reporte["contenido"]
        if isinstance(datos, str):
            datos = json.loads(datos)

        libro = Workbook()
        hoja = libro.active
        hoja.title = "Reporte RIUL"

        hoja.append([reporte["nombre_reporte"]])
        hoja.append(["Periodo", reporte["periodo"]])
        hoja.append([])
        hoja.append(["USUARIOS"])
        hoja.append(["Total", datos["usuarios"]["total"]])
        hoja.append(["Activos", datos["usuarios"]["activos"]])
        hoja.append(["Rol", "Cantidad"])

        for item in datos["usuarios"]["por_rol"]:
            hoja.append([item["rol"], item["total"]])

        hoja.append([])
        hoja.append(["SEMILLEROS"])
        hoja.append(["Total", datos["semilleros"]["total"]])
        hoja.append(["Activos", datos["semilleros"]["activos"]])

        hoja.append([])
        hoja.append(["PROYECTOS POR FACULTAD"])
        hoja.append(["Facultad", "Cantidad"])

        for item in datos["proyectos_por_facultad"]:
            hoja.append([item["facultad"], item["total"]])

        hoja.append([])
        hoja.append(["LOGROS POR ESTADO"])
        hoja.append(["Estado", "Cantidad"])

        for item in datos["logros"]:
            hoja.append([item["estado"], item["total"]])

        hoja.append([])
        hoja.append(["XP ACREDITADO", datos["xp_acreditado"]])

        archivo = BytesIO()
        libro.save(archivo)
        archivo.seek(0)

        return send_file(
            archivo,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"reporte_RIUL_{id_reporte}.xlsx"
        )

    except Exception as error:
        db.session.rollback()
        print("ERROR EXCEL:", repr(error))
        return jsonify({"mensaje": "No fue posible generar Excel."}), 500
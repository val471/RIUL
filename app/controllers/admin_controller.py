
from flask import render_template, jsonify
from sqlalchemy import text
from app.extensions import db


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


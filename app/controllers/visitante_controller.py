from flask import render_template
from sqlalchemy import text
from app.extensions import db


def _consultar(sql, parametros=None):
    """Ejecuta una consulta de la pantalla pública.
    Si falla, devuelve lista vacía para que la página nunca se caiga."""
    try:
        return db.session.execute(text(sql), parametros or {}).mappings().all()
    except Exception as error:
        db.session.rollback()
        print("ERROR PANTALLA DE BIENVENIDA:", repr(error))
        return []


def _contar(sql):
    filas = _consultar(sql)
    return list(filas[0].values())[0] if filas else 0


def inicio():
    estadisticas = {
        "investigadores": _contar("""
            SELECT COUNT(*) FROM usuario
            WHERE estado = 'ACTIVO'
              AND rol IN ('ESTUDIANTE', 'DOCENTE', 'DOCENTE_LIDER')
        """),
        "semilleros": _contar(
            "SELECT COUNT(*) FROM semillero WHERE estado = 'ACTIVO'"
        ),
        "proyectos": _contar("SELECT COUNT(*) FROM proyecto"),
    }

    semilleros = _consultar("""
        SELECT
            s.nombre,
            s.linea_investigacion,
            f.nombre AS facultad,
            (SELECT COUNT(*) FROM membresiasemillero m
             WHERE m.id_semillero = s.id_semillero
               AND m.fecha_salida IS NULL) AS integrantes,
            (SELECT COUNT(*) FROM proyecto p
             WHERE p.id_semillero = s.id_semillero) AS proyectos
        FROM semillero s
        INNER JOIN facultad f ON f.id_facultad = s.id_facultad
        WHERE s.estado = 'ACTIVO'
        ORDER BY s.fecha_creacion DESC, s.id_semillero DESC
        LIMIT 3
    """)

    proyectos = _consultar("""
        SELECT p.titulo, p.estado, s.nombre AS semillero
        FROM proyecto p
        INNER JOIN semillero s ON s.id_semillero = p.id_semillero
        ORDER BY p.fecha_inicio DESC, p.id_proyecto DESC
        LIMIT 3
    """)

    eventos = _consultar("""
        SELECT nombre, descripcion, lugar, fecha
        FROM evento
        WHERE fecha >= NOW()
        ORDER BY fecha ASC
        LIMIT 3
    """)

    facultades = _consultar(
        "SELECT nombre FROM facultad ORDER BY nombre"
    )

    categorias = _consultar("""
        SELECT DISTINCT linea_investigacion AS nombre
        FROM semillero
        WHERE estado = 'ACTIVO'
          AND linea_investigacion IS NOT NULL
          AND linea_investigacion <> ''
        ORDER BY linea_investigacion
    """)

    return render_template(
        "index.html",
        estadisticas=estadisticas,
        semilleros=semilleros,
        proyectos=proyectos,
        eventos=eventos,
        facultades=facultades,
        categorias=categorias,
    )


def semilleros():
    return render_template("visitante/semilleros.html")


def proyectos():
    return render_template("visitante/proyectos.html")


def eventos():
    return render_template("visitante/eventos.html")


def contacto():
    return render_template("visitante/contacto.html")
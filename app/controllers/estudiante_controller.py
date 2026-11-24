
from flask import render_template, session
from flask import request, jsonify, current_app
from sqlalchemy import text
from app.extensions import db
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
import re
import time


# =====================================================
# PANEL DEL ESTUDIANTE
# =====================================================

def _escalar(consulta, parametros):
    return db.session.execute(text(consulta), parametros).scalar() or 0


def mostrar_panel():
    id_estudiante = obtener_id_estudiante()
    perfil = obtener_perfil()

    nombre = (perfil.get("nombre_institucional") or "Estudiante").strip()
    partes = nombre.split()
    primer_nombre = partes[0] if partes else "Estudiante"
    iniciales = "".join(p[0] for p in partes[:2]).upper() or "E"

    p = {"id": id_estudiante}

    total_insignias = _escalar(
        "SELECT COUNT(*) FROM insigniaotorgada WHERE id_usuario = :id", p)

    xp_total = _escalar(
        "SELECT xp_total FROM estudianteinvestigador WHERE id_usuario = :id", p)

    total_logros = _escalar(
        "SELECT COUNT(*) FROM logro "
        "WHERE id_estudiante = :id AND estado = 'APROBADO'", p)

    total_semilleros = _escalar(
        "SELECT COUNT(*) FROM membresiasemillero "
        "WHERE id_estudiante = :id AND fecha_salida IS NULL", p)

    estrellas = _escalar(
        "SELECT n.estrellas FROM estudianteinvestigador ei "
        "JOIN nivel n ON n.id_nivel = ei.id_nivel_actual "
        "WHERE ei.id_usuario = :id", p)

    # Insignias que faltan para el siguiente nivel
    minimas_siguiente = db.session.execute(text("""
        SELECT MIN(insignias_minimas) FROM nivel
        WHERE insignias_minimas > :total
    """), {"total": total_insignias}).scalar()

    faltan_insignias = (
        max(minimas_siguiente - total_insignias, 0)
        if minimas_siguiente is not None else 0
    )

    return render_template(
        "estudiante/index.html",
        nombre_completo=nombre,
        primer_nombre=primer_nombre,
        iniciales=iniciales,
        total_insignias=total_insignias,
        faltan_insignias=faltan_insignias,
        xp_total=xp_total,
        total_logros=total_logros,
        total_semilleros=total_semilleros,
        estrellas=min(int(estrellas), 5)
    )
# =====================================================
# IDENTIFICACION DEL ESTUDIANTE
# =====================================================

def obtener_id_estudiante():
    return session.get("id_usuario")


# =====================================================
# PERFIL DEL ESTUDIANTE
# =====================================================

def obtener_perfil():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return {}

    perfil = db.session.execute(text("""
        SELECT
            u.id_usuario,
            u.nombre_institucional,
            u.correo_institucional,
            u.fecha_nacimiento,
            u.foto_perfil,
            u.telefono,
            u.documento,
            ei.codigo_estudiantil,
            ei.semestre,
            p.nombre AS programa,
            f.nombre AS facultad
        FROM usuario u
        LEFT JOIN estudianteinvestigador ei
            ON ei.id_usuario = u.id_usuario
        LEFT JOIN programa p
            ON p.id_programa = ei.id_programa
        LEFT JOIN facultad f
            ON f.id_facultad = p.id_facultad
        WHERE u.id_usuario = :id_usuario
          AND u.rol = 'ESTUDIANTE'
    """), {
        "id_usuario": id_estudiante
    }).mappings().first()

    return dict(perfil) if perfil else {}


def mostrar_perfil():

    datos = obtener_perfil()

    return render_template(
        "estudiante/perfil.html",
        perfil=datos
    )


# =====================================================
# SOLICITAR CAMBIOS DEL PERFIL
# =====================================================

def solicitar_cambio_perfil():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return jsonify({
            "mensaje": "No se encontró tu usuario."
        }), 401

    datos = request.get_json(silent=True) or {}

    campo = (datos.get("campo") or "").strip()
    valor_nuevo = (datos.get("valor_nuevo") or "").strip()
    descripcion = (datos.get("descripcion") or "").strip()

    campos_permitidos = {
        "nombre": "nombre_institucional",
        "correo": "correo_institucional",
        "fecha_nacimiento": "fecha_nacimiento",
        "telefono": "telefono",
        "facultad": "facultad",
        "programa": "programa",
        "codigo_estudiantil": "codigo_estudiantil",
        "semestre": "semestre"
    }

    if campo not in campos_permitidos:
        return jsonify({
            "mensaje": "El dato seleccionado no es válido."
        }), 400

    if not valor_nuevo or not descripcion:
        return jsonify({
            "mensaje": "Completa el nuevo dato y explica el motivo de la solicitud."
        }), 400

    if len(valor_nuevo) > 255:
        return jsonify({
            "mensaje": "El nuevo dato es demasiado largo."
        }), 400

    if campo == "correo":

        valor_nuevo = valor_nuevo.lower()

        if not re.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            valor_nuevo
        ):
            return jsonify({
                "mensaje": "El correo no tiene un formato válido."
            }), 400

        if not valor_nuevo.endswith("@unilibre.edu.co"):
            return jsonify({
                "mensaje": "Debes utilizar tu correo institucional."
            }), 400

    try:

        perfil = obtener_perfil()

        if not perfil:
            return jsonify({
                "mensaje": "No se encontró el perfil."
            }), 404

        campo_bd = campos_permitidos[campo]
        valor_anterior = perfil.get(campo_bd)

        if valor_anterior is None:
            valor_anterior = perfil.get(campo, "")

        valor_anterior = str(valor_anterior or "")

        if valor_nuevo == valor_anterior:
            return jsonify({
                "mensaje": "El nuevo dato es igual al que ya tienes registrado."
            }), 400

        pendiente = db.session.execute(text("""
            SELECT id_solicitud_act
            FROM solicitudactualizacion
            WHERE id_usuario = :id
              AND campo_modificado = :campo
              AND estado = 'PENDIENTE'
            LIMIT 1
        """), {
            "id": id_estudiante,
            "campo": campo_bd
        }).first()

        if pendiente:
            return jsonify({
                "mensaje": "Ya tienes una solicitud pendiente para este dato."
            }), 409

        db.session.execute(text("""
            INSERT INTO solicitudactualizacion (
                id_usuario,
                campo_modificado,
                valor_anterior,
                valor_nuevo,
                descripcion_solicitud,
                estado,
                fecha_solicitud
            )
            VALUES (
                :id_usuario,
                :campo,
                :anterior,
                :nuevo,
                :descripcion,
                'PENDIENTE',
                NOW()
            )
        """), {
            "id_usuario": id_estudiante,
            "campo": campo_bd,
            "anterior": valor_anterior or None,
            "nuevo": valor_nuevo,
            "descripcion": descripcion
        })

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
    "id_usuario": id_estudiante,
    "mensaje": "Tu solicitud de cambio de perfil fue enviada y está pendiente de aprobación."
})
        db.session.commit()

        return jsonify({
            "mensaje": "Tu solicitud fue enviada correctamente y está pendiente de aprobación."
        }), 201

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Error al registrar solicitud de cambio de perfil"
        )

        return jsonify({
            "mensaje": "No fue posible enviar tu solicitud."
        }), 500


# =====================================================
# CAMBIAR CONTRASEÑA
# =====================================================

def cambiar_contrasena():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return jsonify({
            "mensaje": "No se encontró tu usuario."
        }), 401

    datos = request.get_json(silent=True) or {}

    actual = datos.get("actual") or ""
    nueva = datos.get("nueva") or ""
    confirmar = datos.get("confirmar") or ""

    usuario = db.session.execute(text("""
        SELECT contrasena_hash
        FROM usuario
        WHERE id_usuario = :id
          AND rol = 'ESTUDIANTE'
    """), {
        "id": id_estudiante
    }).mappings().first()

    if not usuario:
        return jsonify({
            "mensaje": "No se encontró tu cuenta."
        }), 404

    if not check_password_hash(
        usuario["contrasena_hash"],
        actual
    ):
        return jsonify({
            "mensaje": "La contraseña actual no es correcta."
        }), 400

    if len(nueva) < 8:
        return jsonify({
            "mensaje": "La nueva contraseña debe tener mínimo 8 caracteres."
        }), 400

    if nueva != confirmar:
        return jsonify({
            "mensaje": "Las contraseñas no coinciden."
        }), 400

    if check_password_hash(
        usuario["contrasena_hash"],
        nueva
    ):
        return jsonify({
            "mensaje": "La nueva contraseña debe ser diferente a la actual."
        }), 400

    try:

        db.session.execute(text("""
            UPDATE usuario
            SET contrasena_hash = :nueva,
                fecha_actualizacion = NOW()
            WHERE id_usuario = :id
        """), {
            "nueva": generate_password_hash(nueva),
            "id": id_estudiante
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Tu contraseña fue actualizada correctamente."
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Error al cambiar contraseña del estudiante"
        )

        return jsonify({
            "mensaje": "No fue posible actualizar tu contraseña."
        }), 500


# =====================================================
# LOGROS DEL ESTUDIANTE
# =====================================================

def mostrar_logros():

    datos = cargar_logros()

    return render_template(
        "estudiante/logros.html",
        tipos_logro=datos["tipos"],
        mis_logros=datos["logros"]
    )


def obtener_tipos_logro():

    tipos = db.session.execute(text("""
        SELECT
            id_tipo_logro,
            nombre,
            xp_otorgado
        FROM tipologro
        ORDER BY id_tipo_logro
    """)).mappings().all()

    return [dict(tipo) for tipo in tipos]


def cargar_logros():

    id_estudiante = obtener_id_estudiante()

    tipos = obtener_tipos_logro()
    logros = obtener_mis_logros(id_estudiante)

    return {
        "tipos": tipos,
        "logros": logros
    }


def obtener_mis_logros(id_estudiante):

    logros = db.session.execute(text("""
        SELECT
            l.id_logro,
            l.titulo,
            l.descripcion,
            l.estado,
            l.fecha_registro,
            tl.nombre AS tipo_logro,
            tl.xp_otorgado
        FROM logro l
        INNER JOIN tipologro tl
            ON l.id_tipo_logro = tl.id_tipo_logro
        WHERE l.id_estudiante = :id_estudiante
        ORDER BY l.fecha_registro DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [dict(logro) for logro in logros]


# =====================================================
# REGISTRAR LOGRO
# =====================================================

def registrar_logro():

    try:

        id_estudiante = obtener_id_estudiante()

        id_tipo_logro = request.form.get("id_tipo_logro")
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        archivo = request.files.get("evidencia")

        if not id_estudiante or not id_tipo_logro or not titulo:
            return jsonify({
                "exito": False,
                "mensaje": "Completa los campos obligatorios."
            }), 400

        if not archivo or archivo.filename == "":
            return jsonify({
                "exito": False,
                "mensaje": "Debes adjuntar una evidencia."
            }), 400

        extension = archivo.filename.rsplit(".", 1)[-1].lower()

        if extension not in {"pdf", "png"}:
            return jsonify({
                "exito": False,
                "mensaje": "Solo se permiten archivos PDF o PNG."
            }), 400

        carpeta = os.path.join(
            current_app.root_path,
            "static",
            "uploads",
            "evidencias"
        )

        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = secure_filename(archivo.filename)

        nombre_final = (
            f"{id_estudiante}_{int(datetime.now().timestamp())}_"
            f"{nombre_archivo}"
        )

        ruta_archivo = os.path.join(
            carpeta,
            nombre_final
        )

        archivo.save(ruta_archivo)

        resultado = db.session.execute(text("""
            INSERT INTO logro (
                id_tipo_logro,
                titulo,
                descripcion,
                id_estudiante,
                estado,
                fecha_registro
            )
            VALUES (
                :tipo,
                :titulo,
                :descripcion,
                :estudiante,
                'PENDIENTE',
                :fecha
            )
        """), {
            "tipo": id_tipo_logro,
            "titulo": titulo,
            "descripcion": descripcion,
            "estudiante": id_estudiante,
            "fecha": datetime.now()
        })

        id_logro = resultado.lastrowid

        db.session.execute(text("""
            INSERT INTO evidencia (
                id_logro,
                descripcion,
                fecha_registro,
                archivo
            )
            VALUES (
                :logro,
                :descripcion,
                :fecha,
                :archivo
            )
        """), {
            "logro": id_logro,
            "descripcion": "Evidencia adjunta",
            "fecha": datetime.now(),
            "archivo": f"uploads/evidencias/{nombre_final}"
        })

        db.session.commit()

        return jsonify({
            "exito": True,
            "mensaje": "Logro registrado correctamente."
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Error al registrar logro"
        )

        return jsonify({
            "exito": False,
            "mensaje": "No se pudo registrar el logro."
        }), 500


# =====================================================
# HOJA DE VIDA INVESTIGATIVA
# =====================================================

def obtener_logros_hoja_vida(id_estudiante):

    logros = db.session.execute(text("""
        SELECT
            l.titulo,
            l.descripcion AS detalle,
            tl.nombre AS tipo_logro,
            l.fecha_registro
        FROM logro l
        INNER JOIN tipologro tl
            ON l.id_tipo_logro = tl.id_tipo_logro
        WHERE l.id_estudiante = :id_estudiante
          AND l.estado = 'APROBADO'
        ORDER BY l.fecha_registro DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [dict(logro) for logro in logros]


def cargar_hoja_vida():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return {}

    datos = {
        "perfil": obtener_datos_basicos_hoja_vida(id_estudiante),
        "logros": obtener_logros_hoja_vida(id_estudiante),
        "semilleros": obtener_semillero_hoja_vida(id_estudiante),
        "eventos": obtener_eventos_hoja_vida(id_estudiante),
        "publicaciones": obtener_publicaciones_hoja_vida(id_estudiante),
        "proyectos": obtener_proyectos_hoja_vida(id_estudiante),
        "insignias": obtener_insignias_hoja_vida(id_estudiante),
    }

    return datos

def obtener_hoja_vida():

    datos = cargar_hoja_vida()

    return jsonify(datos)
def obtener_datos_basicos_hoja_vida(id_estudiante):

    resultado = db.session.execute(text("""
        SELECT
            u.nombre_institucional AS nombre,
            u.correo_institucional AS correo,
            u.fecha_nacimiento,
            u.foto_perfil,
            u.telefono,
            p.nombre AS programa,
            ei.semestre,
            ei.xp_total,
            n.nombre AS nivel,
            n.estrellas
        FROM usuario u
        INNER JOIN estudianteinvestigador ei
            ON u.id_usuario = ei.id_usuario
        INNER JOIN programa p
            ON ei.id_programa = p.id_programa
        LEFT JOIN nivel n
            ON ei.id_nivel_actual = n.id_nivel
        WHERE u.id_usuario = :id_estudiante
    """), {
        "id_estudiante": id_estudiante
    }).mappings().first()

    if not resultado:
        return {}

    datos = dict(resultado)

    datos["fecha_nacimiento"] = (
        resultado["fecha_nacimiento"].strftime("%d/%m/%Y")
        if resultado["fecha_nacimiento"] else ""
    )

    return datos

def obtener_semillero_hoja_vida(id_estudiante):

    resultado = db.session.execute(text("""
        SELECT
            s.nombre,
            s.descripcion,
            s.linea_investigacion,
            s.fecha_creacion
        FROM estudianteinvestigador ei
        INNER JOIN semillero s
            ON ei.id_semillero = s.id_semillero
        WHERE ei.id_usuario = :id_estudiante
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [dict(fila) for fila in resultado]
def obtener_eventos_hoja_vida(id_estudiante):

    resultados = db.session.execute(text("""
        SELECT
            e.nombre,
            e.descripcion,
            e.fecha,
            e.lugar,
            e.modalidad,
            pe.tipo_participacion
        FROM participacionevento pe
        INNER JOIN evento e
            ON pe.id_evento = e.id_evento
        WHERE pe.id_usuario = :id_estudiante
        ORDER BY e.fecha DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [
    {
        **dict(fila),
        "fecha": (
            fila["fecha"].strftime("%d/%m/%Y")
            if fila["fecha"] else ""
        )
    }
    for fila in resultados
]

def obtener_publicaciones_hoja_vida(id_estudiante):

    resultados = db.session.execute(text("""
        SELECT
            contenido,
            categoria,
            tipo_publicacion,
            fecha_publicacion
        FROM publicacion
        WHERE id_usuario = :id_estudiante
        ORDER BY fecha_publicacion DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [dict(fila) for fila in resultados]

def obtener_proyectos_hoja_vida(id_estudiante):

    resultados = db.session.execute(text("""
        SELECT
            p.titulo,
            p.descripcion,
            p.fecha_inicio,
            p.estado,
            s.nombre AS semillero
        FROM estudianteinvestigador ei
        INNER JOIN proyecto p
            ON ei.id_semillero = p.id_semillero
        INNER JOIN semillero s
            ON p.id_semillero = s.id_semillero
        WHERE ei.id_usuario = :id_estudiante
        ORDER BY p.fecha_inicio DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [
    {
        **dict(fila),
        "fecha_publicacion": (
            fila["fecha_publicacion"].strftime("%d/%m/%Y")
            if fila["fecha_publicacion"] else ""
        )
    }
    for fila in resultados
]
def obtener_insignias_hoja_vida(id_estudiante):

    resultados = db.session.execute(text("""
        SELECT
            i.nombre,
            i.descripcion,
            i.tipo,
            i.grado,
            io.fecha_obtencion
        FROM insigniaotorgada io
        INNER JOIN insignia i
            ON io.id_insignia = i.id_insignia
        WHERE io.id_usuario = :id_estudiante
        ORDER BY io.fecha_obtencion DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [
        {
            "nombre": fila["nombre"],
            "descripcion": fila["descripcion"],
            "tipo": fila["tipo"],
            "grado": fila["grado"],
            "fecha_obtencion": (
                fila["fecha_obtencion"].strftime("%Y-%m-%d")
                if fila["fecha_obtencion"] else ""
            )
        }
        for fila in resultados
    ]



# =====================================================
# PROYECTOS DEL ESTUDIANTE
# =====================================================

def obtener_proyectos_hoja_vida(id_estudiante):

    resultados = db.session.execute(text("""
        SELECT
            p.titulo,
            p.descripcion,
            p.fecha_inicio,
            p.estado,
            s.nombre AS semillero
        FROM estudianteinvestigador ei
        INNER JOIN proyecto p
            ON ei.id_semillero = p.id_semillero
        INNER JOIN semillero s
            ON p.id_semillero = s.id_semillero
        WHERE ei.id_usuario = :id_estudiante
        ORDER BY p.fecha_inicio DESC
    """), {
        "id_estudiante": id_estudiante
    }).mappings().all()

    return [
        {
            **dict(fila),
            "fecha_inicio": (
                fila["fecha_inicio"].strftime("%d/%m/%Y")
                if fila["fecha_inicio"] else ""
            )
        }
        for fila in resultados
    ]

# =====================================================
# EVENTOS DEL ESTUDIANTE
# =====================================================

def obtener_eventos():

    resultados = db.session.execute(text("""
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
    """)).mappings().all()

    return [
        {
            **dict(evento),
            "fecha": (
                evento["fecha"].strftime("%Y-%m-%d %H:%M:%S")
                if evento["fecha"] else None
            ),
            "fecha_cierre": (
                evento["fecha_cierre"].strftime("%Y-%m-%d %H:%M:%S")
                if evento["fecha_cierre"] else None
            )
        }
        for evento in resultados
    ]


def cargar_eventos():
    return jsonify(obtener_eventos())

# =====================================================
# SOLICITUD DE CAMBIO DE FOTO DE PERFIL
# =====================================================


def solicitar_cambio_foto():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return jsonify({"mensaje": "No se encontró tu usuario."}), 401

    archivo = request.files.get("foto")
    descripcion = (request.form.get("descripcion") or "").strip()

    if not archivo or not archivo.filename:
        return jsonify({"mensaje": "Selecciona la foto que quieres usar."}), 400

    if not descripcion:
        return jsonify({"mensaje": "Explica el motivo de la solicitud."}), 400

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
        return jsonify({"mensaje": "La imagen no debe superar 2 MB."}), 400

    ruta_archivo = None

    try:
        pendiente = db.session.execute(text("""
            SELECT 1
            FROM solicitudactualizacion
            WHERE id_usuario = :id
              AND campo_modificado = 'foto_perfil'
              AND estado = 'PENDIENTE'
            LIMIT 1
        """), {"id": id_estudiante}).first()

        if pendiente:
            return jsonify({
                "mensaje": "Ya tienes una solicitud pendiente para tu foto."
            }), 409

        perfil = obtener_perfil() or {}

        carpeta = os.path.join(
            current_app.static_folder,
            "uploads",
            "perfiles"
        )
        os.makedirs(carpeta, exist_ok=True)

        nombre_archivo = (
            f"solicitud_{id_estudiante}_{int(time.time())}.{extension}"
        )
        ruta_archivo = os.path.join(carpeta, nombre_archivo)
        archivo.save(ruta_archivo)

        db.session.execute(text("""
            INSERT INTO solicitudactualizacion (
                id_usuario,
                campo_modificado,
                valor_anterior,
                valor_nuevo,
                descripcion_solicitud,
                estado,
                fecha_solicitud
            )
            VALUES (
                :id_usuario,
                'foto_perfil',
                :anterior,
                :nuevo,
                :descripcion,
                'PENDIENTE',
                NOW()
            )
        """), {
            "id_usuario": id_estudiante,
            "anterior": perfil.get("foto_perfil"),
            "nuevo": "uploads/perfiles/" + nombre_archivo,
            "descripcion": descripcion
        })

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
            "id_usuario": id_estudiante,
            "mensaje": "Tu solicitud de cambio de foto fue enviada y está pendiente de aprobación."
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Tu nueva foto fue enviada y está pendiente de aprobación."
        }), 201

    except Exception:

        db.session.rollback()

        if ruta_archivo and os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

        current_app.logger.exception("Error al solicitar cambio de foto")

        return jsonify({
            "mensaje": "No fue posible enviar la solicitud."
        }), 500


# =====================================================
# PUBLICACIONES GENERALES DEL ESTUDIANTE
# =====================================================

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
            u.rol AS rol_autor,
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
        LIMIT 100
    """), {"yo": yo}).mappings().all()

    archivos = {}
    ids = [f["id_publicacion"] for f in filas]

    if ids:
        marcadores = ", ".join(
            f":p{i}" for i in range(len(ids))
        )
        parametros = {
            f"p{i}": valor
            for i, valor in enumerate(ids)
        }

        filas_archivo = db.session.execute(text(f"""
            SELECT
                id_publicacion,
                nombre_original,
                ruta,
                tipo_archivo
            FROM archivo
            WHERE id_publicacion IN ({marcadores})
            ORDER BY id_archivo ASC
        """), parametros).mappings().all()

        for archivo in filas_archivo:
            archivos.setdefault(archivo["id_publicacion"], {
                "nombre": archivo["nombre_original"],
                "ruta": archivo["ruta"],
                "tipo": archivo["tipo_archivo"]
            })

    total = db.session.execute(text("""
        SELECT COUNT(*) FROM publicacion
    """)).scalar() or 0

    academicas = db.session.execute(text("""
        SELECT COUNT(*)
        FROM publicacion
        WHERE tipo_publicacion = 'ACADEMICA'
    """)).scalar() or 0

    return jsonify({
        "total": total,
        "academicas": academicas,
        "publicaciones": [{
            "id": f["id_publicacion"],
            "autor": f["autor"],
            "rol": f["rol_autor"],
            "semillero": f["semillero"] or "",
            "contenido": f["contenido"],
            "academica": f["tipo_publicacion"] == "ACADEMICA",
            "vistas": f["vistas"],
            "fecha": (
                f["fecha_publicacion"].strftime("%d/%m/%Y %H:%M")
                if f["fecha_publicacion"] else ""
            ),
            "propia": f["id_usuario"] == yo,
            "comentarios": f["comentarios"],
            "reacciones": f["reacciones"],
            "yo_reaccione": bool(f["yo_reaccione"]),
            "archivo": archivos.get(f["id_publicacion"])
        } for f in filas]
    })


def crear_publicacion():
    id_usuario = session.get("id_usuario")

    contenido = (request.form.get("contenido") or "").strip()
    academica = (
        request.form.get("academica") or ""
    ).lower() in {"true", "1", "on"}

    archivo = request.files.get("archivo")

    if not contenido:
        return jsonify({
            "mensaje": "Escribe algo para publicar."
        }), 400

    if len(contenido) > 3000:
        return jsonify({
            "mensaje": "La publicación no puede superar 3000 caracteres."
        }), 400

    extension = ""
    peso = 0

    if archivo and archivo.filename:
        if "." in archivo.filename:
            extension = archivo.filename.rsplit(".", 1)[-1].lower()

        if extension not in {"pdf", "png", "jpg", "jpeg", "webp"}:
            return jsonify({
                "mensaje": "Formato no permitido. Usa PDF, PNG, JPG o WEBP."
            }), 400

        archivo.seek(0, os.SEEK_END)
        peso = archivo.tell()
        archivo.seek(0)

        if peso > 5 * 1024 * 1024:
            return jsonify({
                "mensaje": "El archivo no debe superar 5 MB."
            }), 400

    ruta_disco = None

    try:
        id_semillero = db.session.execute(text("""
            SELECT id_semillero
            FROM estudianteinvestigador
            WHERE id_usuario = :usuario
        """), {"usuario": id_usuario}).scalar()

        resultado = db.session.execute(text("""
            INSERT INTO publicacion (
                id_usuario,
                id_semillero,
                contenido,
                tipo_publicacion,
                vistas,
                fecha_publicacion,
                fecha_actualizacion
            )
            VALUES (
                :usuario,
                :semillero,
                :contenido,
                :tipo,
                0,
                NOW(),
                NOW()
            )
        """), {
            "usuario": id_usuario,
            "semillero": id_semillero,
            "contenido": contenido,
            "tipo": "ACADEMICA" if academica else "GENERAL"
        })

        id_publicacion = resultado.lastrowid

        if archivo and archivo.filename:
            carpeta = os.path.join(
                current_app.static_folder,
                "uploads",
                "publicaciones"
            )
            os.makedirs(carpeta, exist_ok=True)

            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = (
                f"pub_{id_publicacion}_{int(time.time())}.{extension}"
            )

            ruta_disco = os.path.join(carpeta, nombre_final)
            archivo.save(ruta_disco)

            db.session.execute(text("""
                INSERT INTO archivo (
                    id_usuario,
                    id_publicacion,
                    nombre_original,
                    ruta,
                    tipo_archivo,
                    peso_archivo,
                    fecha_carga,
                    fecha_actualizacion
                )
                VALUES (
                    :usuario,
                    :publicacion,
                    :nombre,
                    :ruta,
                    :tipo,
                    :peso,
                    NOW(),
                    NOW()
                )
            """), {
                "usuario": id_usuario,
                "publicacion": id_publicacion,
                "nombre": nombre_seguro[:150],
                "ruta": f"/static/uploads/publicaciones/{nombre_final}",
                "tipo": extension,
                "peso": peso
            })

        db.session.commit()

        return jsonify({
            "mensaje": "Publicación creada correctamente.",
            "id": id_publicacion
        }), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR PUBLICACION ESTUDIANTE:", repr(error))

        if ruta_disco and os.path.exists(ruta_disco):
            os.remove(ruta_disco)

        return jsonify({
            "mensaje": "No fue posible guardar la publicación."
        }), 500


def reaccionar_publicacion(id_publicacion):
    yo = session.get("id_usuario")

    try:
        existe = db.session.execute(text("""
            SELECT 1
            FROM publicacion
            WHERE id_publicacion = :id
        """), {"id": id_publicacion}).first()

        if not existe:
            return jsonify({
                "mensaje": "La publicación no existe."
            }), 404

        reaccion = db.session.execute(text("""
            SELECT id_reaccion
            FROM reaccion
            WHERE id_publicacion = :publicacion
              AND id_usuario = :usuario
        """), {
            "publicacion": id_publicacion,
            "usuario": yo
        }).first()

        if reaccion:
            db.session.execute(text("""
                DELETE FROM reaccion
                WHERE id_publicacion = :publicacion
                  AND id_usuario = :usuario
            """), {
                "publicacion": id_publicacion,
                "usuario": yo
            })
        else:
            db.session.execute(text("""
                INSERT INTO reaccion (
                    id_publicacion,
                    id_usuario,
                    fecha
                )
                VALUES (:publicacion, :usuario, NOW())
            """), {
                "publicacion": id_publicacion,
                "usuario": yo
            })

        db.session.commit()

        total = db.session.execute(text("""
            SELECT COUNT(*)
            FROM reaccion
            WHERE id_publicacion = :id
        """), {"id": id_publicacion}).scalar() or 0

        return jsonify({
            "reaccionado": not bool(reaccion),
            "total": total
        })

    except Exception as error:
        db.session.rollback()
        print("ERROR REACCION PUBLICACION:", repr(error))

        return jsonify({
            "mensaje": "No fue posible registrar la reacción."
        }), 500


def obtener_comentarios_publicacion(id_publicacion):
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
        "fecha": (
            f["fecha"].strftime("%d/%m/%Y %H:%M")
            if f["fecha"] else ""
        )
    } for f in filas])


def crear_comentario_publicacion(id_publicacion):
    datos = request.get_json(silent=True) or {}
    contenido = (datos.get("contenido") or "").strip()

    if not contenido:
        return jsonify({
            "mensaje": "Escribe un comentario."
        }), 400

    if len(contenido) > 1000:
        return jsonify({
            "mensaje": "El comentario no puede superar 1000 caracteres."
        }), 400

    try:
        existe = db.session.execute(text("""
            SELECT 1
            FROM publicacion
            WHERE id_publicacion = :id
        """), {"id": id_publicacion}).first()

        if not existe:
            return jsonify({
                "mensaje": "La publicación no existe."
            }), 404

        db.session.execute(text("""
            INSERT INTO comentario (
                id_publicacion,
                id_usuario,
                contenido,
                fecha,
                fecha_actualizacion
            )
            VALUES (
                :publicacion,
                :usuario,
                :contenido,
                NOW(),
                NOW()
            )
        """), {
            "publicacion": id_publicacion,
            "usuario": session.get("id_usuario"),
            "contenido": contenido
        })

        db.session.commit()

        return jsonify({
            "mensaje": "Comentario publicado."
        }), 201

    except Exception as error:
        db.session.rollback()
        print("ERROR COMENTARIO PUBLICACION:", repr(error))

        return jsonify({
            "mensaje": "No fue posible guardar el comentario."
        }), 500

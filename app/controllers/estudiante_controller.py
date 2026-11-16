
from flask import render_template, session
from flask import request, jsonify, current_app
from sqlalchemy import text
from app.extensions import db
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import os
import re


# =====================================================
# PANEL DEL ESTUDIANTE
# =====================================================

def mostrar_panel():
    return render_template("estudiante/index.html")


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

def cambiar_contraseña():

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

def obtener_mis_proyectos():

    id_estudiante = obtener_id_estudiante()

    if not id_estudiante:
        return jsonify({
            "proyectos": []
        }), 401

    try:

        consulta = text("""
            SELECT
                p.id_proyecto,
                p.titulo,
                p.descripcion,
                p.fecha_inicio,
                p.estado,
                s.nombre AS semillero
            FROM estudianteinvestigador ei
            INNER JOIN proyecto p
                ON p.id_semillero = ei.id_semillero
            INNER JOIN semillero s
                ON s.id_semillero = ei.id_semillero
            WHERE ei.id_usuario = :id_estudiante
            ORDER BY p.fecha_inicio DESC
        """)

        resultados = db.session.execute(
            consulta,
            {"id_estudiante": id_estudiante}
        ).mappings().all()

        proyectos = []

        for fila in resultados:

            proyectos.append({
                "id_proyecto": fila["id_proyecto"],
                "titulo": fila["titulo"],
                "descripcion": fila["descripcion"],
                "fecha_inicio": (
                    fila["fecha_inicio"].strftime("%Y-%m-%d")
                    if fila["fecha_inicio"] else ""
                ),
                "estado": fila["estado"],
                "semillero": fila["semillero"]
            })

        return jsonify({
            "proyectos": proyectos
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Error al consultar los proyectos del estudiante"
        )

        return jsonify({
            "proyectos": [],
            "mensaje": "No fue posible consultar tus proyectos."
        }), 500

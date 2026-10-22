
from flask import jsonify


def validar_cuenta_demo(correo, contrasena):
    """
    Valida las cuentas ficticias de demostración.
    No consulta ni modifica la base de datos.
    """

    cuentas_demo = {
        "admin@unilibre.edu.co": {
            "contrasena": "Admin123!",
            "rol": "ADMIN",
            "destino": "/admin",
        },
        "estudiante@unilibre.edu.co": {
            "contrasena": "Estudiante123!",
            "rol": "ESTUDIANTE",
            "destino": "/estudiante",
        },
        "docente@unilibre.edu.co": {
            "contrasena": "Docente123!",
            "rol": "DOCENTE",
            "destino": "/docente",
        },
    }

    correo = (correo or "").strip().lower()
    cuenta = cuentas_demo.get(correo)

    if not cuenta or cuenta["contrasena"] != (contrasena or ""):
        return {
            "valido": False,
            "mensaje": "Las credenciales no coinciden con las cuentas de prueba.",
        }

    return {
        "valido": True,
        "rol": cuenta["rol"],
        "destino": cuenta["destino"],
        "mensaje": "Acceso de demostración correcto.",
    }


def registro_demo():
    """
    Informa que el registro está deshabilitado.
    No crea ni guarda usuarios.
    """
    return jsonify({
        "registrado": False,
        "mensaje": (
            "El registro no está habilitado en esta versión "
            "de demostración. No se guardaron datos."
        ),
    }), 403

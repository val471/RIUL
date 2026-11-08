from werkzeug.security import generate_password_hash
from sqlalchemy import text
from app import create_app
from app.extensions import db

USUARIOS = [
    ("Administrador General", "admin@unilibre.edu.co", "Admin123!", "ADMIN"),
    ("Andrés Martínez", "estudiante@unilibre.edu.co", "Estudiante123!", "ESTUDIANTE"),
    ("Docente Demo", "docente@unilibre.edu.co", "Docente123!", "DOCENTE"),
]

app = create_app()
with app.app_context():
    for nombre, correo, clave, rol in USUARIOS:
        db.session.execute(text("""
            INSERT INTO usuario
              (nombre_institucional, correo_institucional, contrasena_hash,
               fecha_nacimiento, rol, estado, fecha_registro)
            VALUES (:n, :c, :h, '2000-01-01', :r, 'ACTIVO', NOW())
            ON DUPLICATE KEY UPDATE
              contrasena_hash = VALUES(contrasena_hash),
              rol = VALUES(rol), estado = 'ACTIVO'
        """), {"n": nombre, "c": correo, "h": generate_password_hash(clave), "r": rol})
    db.session.commit()
    print("Usuarios creados:", len(USUARIOS))
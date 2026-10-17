from app.extensions import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre_institucional = db.Column(db.String(150), nullable=False)
    correo_institucional = db.Column(
        db.String(150), unique=True, nullable=False
    )
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_registro = db.Column(db.DateTime)
    foto_perfil = db.Column(db.String(255))
    telefono = db.Column(db.String(20))

from app.extensions import db


class SolicitudRegistro(db.Model):
    __tablename__ = "solicitudregistro"

    id_solicitud = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    correo_institucional = db.Column(db.String(120), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)

    documento = db.Column(db.String(30), nullable=True)
    id_facultad = db.Column(db.Integer, nullable=True)
    id_programa = db.Column(db.Integer, nullable=True)
    contrasena_hash = db.Column(db.String(255), nullable=True)

    rol_solicitado = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, nullable=False)
    fecha_resolucion = db.Column(db.DateTime, nullable=True)

    id_admin_revisor = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_usuario"),
        nullable=True
    )

    id_usuario_generado = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=True
    )


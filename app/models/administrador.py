from app.extensions import db


class Administrador(db.Model):
    __tablename__ = "administrador"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    codigo_administrador = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=True
    )
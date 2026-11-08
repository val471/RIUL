
from app.extensions import db


class Docente(db.Model):
    __tablename__ = "docente"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    codigo_docente = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    fecha_actualizacion = db.Column(
        db.DateTime,
        nullable=True
    )

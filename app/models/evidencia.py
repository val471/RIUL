from app.extensions import db
from datetime import datetime


class Evidencia(db.Model):
    __tablename__ = "evidencia"

    id_evidencia = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_logro = db.Column(
        db.Integer,
        db.ForeignKey("logro.id_logro"),
        nullable=False
    )

    descripcion = db.Column(
        db.String(100),
        nullable=True
    )

    fecha_registro = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    archivo = db.Column(
        db.String(255),
        nullable=True
    )

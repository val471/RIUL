from app.extensions import db
from datetime import datetime


class MembresiaSemillero(db.Model):
    __tablename__ = "membresiasemillero"

    id_membresia = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    id_estudiante = db.Column(
        db.Integer,
        db.ForeignKey("estudianteinvestigador.id_usuario"),
        nullable=False
    )

    id_semillero = db.Column(
        db.Integer,
        db.ForeignKey("semillero.id_semillero"),
        nullable=False
    )

    fecha_ingreso = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now
    )

    fecha_salida = db.Column(
        db.DateTime,
        nullable=True
    )
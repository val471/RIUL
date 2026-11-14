
from app.extensions import db
from datetime import datetime


class Semillero(db.Model):
    __tablename__ = "semillero"

    id_semillero = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    linea_investigacion = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(20), nullable=False)
    cupo_maximo = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    id_facultad = db.Column(db.Integer, db.ForeignKey("facultad.id_facultad"), nullable=False)
    xp_total = db.Column(db.Integer, nullable=False, default=0)
    id_nivel_actual = db.Column(db.Integer, db.ForeignKey("nivel.id_nivel"), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, nullable=True)

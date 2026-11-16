
from app.extensions import db


class SolicitudActualizacion(db.Model):
    __tablename__ = "solicitudactualizacion"

    id_solicitud_act = db.Column(db.Integer, primary_key=True)

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    campo_modificado = db.Column(db.String(50), nullable=False)
    valor_anterior = db.Column(db.String(255))
    valor_nuevo = db.Column(db.String(255), nullable=False)

    descripcion_solicitud = db.Column(db.Text)

    estado = db.Column(db.String(20), nullable=False)
    fecha_solicitud = db.Column(db.DateTime, nullable=False)
    fecha_resolucion = db.Column(db.DateTime)

    id_admin_revisor = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_usuario")
    )

    motivo_rechazo = db.Column(db.String(255))

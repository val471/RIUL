
from app.extensions import db


class Logro(db.Model):
    __tablename__ = "logro"

    id_logro = db.Column(db.Integer, primary_key=True, autoincrement=True)

    id_tipo_logro = db.Column(
        db.Integer,
        db.ForeignKey("tipologro.id_tipo_logro"),
        nullable=False
    )

    titulo = db.Column(db.String(150), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)

    id_estudiante = db.Column(
        db.Integer,
        db.ForeignKey("estudianteinvestigador.id_usuario"),
        nullable=True
    )

    id_semillero = db.Column(
        db.Integer,
        db.ForeignKey("semillero.id_semillero"),
        nullable=True
    )

    id_docente_registrador = db.Column(
        db.Integer,
        db.ForeignKey("docentelider.id_usuario"),
        nullable=True
    )

    porcentaje_calidad = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(20), nullable=False)

    id_admin_validador = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_usuario"),
        nullable=True
    )

    fecha_registro = db.Column(db.DateTime, nullable=False)
    fecha_validacion = db.Column(db.DateTime, nullable=True)

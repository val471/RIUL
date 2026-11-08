from app.extensions import db


class EstudianteInvestigador(db.Model):
    __tablename__ = "estudianteinvestigador"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    codigo_estudiantil = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    id_programa = db.Column(
        db.Integer,
        db.ForeignKey("programa.id_programa"),
        nullable=False
    )

    semestre = db.Column(db.Integer, nullable=False)

    id_semillero = db.Column(
        db.Integer,
        db.ForeignKey("semillero.id_semillero"),
        nullable=True
    )

    xp_total = db.Column(db.Integer, nullable=False, default=0)

    id_nivel_actual = db.Column(
        db.Integer,
        db.ForeignKey("nivel.id_nivel"),
        nullable=True
    )

    fecha_actualizacion = db.Column(db.DateTime, nullable=True)
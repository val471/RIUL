
from app.extensions import db


class DocenteLider(db.Model):
    __tablename__ = "docentelider"

    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    id_semillero_liderado = db.Column(
        db.Integer,
        db.ForeignKey("semillero.id_semillero"),
        unique=True,
        nullable=True
    )

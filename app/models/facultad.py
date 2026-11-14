from app.extensions import db


class Facultad(db.Model):
    __tablename__ = "facultad"

    id_facultad = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_admin_gestor = db.Column(
        db.Integer,
        db.ForeignKey("administrador.id_usuario"),
        nullable=True
    )
documento = db.Column(db.String(30), nullable=True)

id_facultad = db.Column(db.Integer, nullable=True)

id_programa = db.Column(db.Integer, nullable=True)

contrasena_hash = db.Column(db.String(255), nullable=True)
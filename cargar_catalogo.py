from sqlalchemy import text

# (nombre, xp_otorgado, limite_semanal)
TIPOS_LOGRO = [
    ("Publicación", 5, 3),
    ("Evento", 50, None),
    ("Ponencia", 100, None),
    ("Artículo", 150, None),
    ("Proyecto", 200, None),
    ("Patente", 300, None),
]

# (nombre, estrellas, insignias_minimas, tipo)
NIVELES = [
    ("Explorador", 1, 1, "ESTUDIANTE"),
    ("Aprendiz", 2, 5, "ESTUDIANTE"),
    ("Investigador", 3, 10, "ESTUDIANTE"),
    ("Experto", 4, 15, "ESTUDIANTE"),
    ("Maestro", 5, 20, "ESTUDIANTE"),
    ("Emergente", 1, 1, "SEMILLERO"),
    ("En Desarrollo", 2, 5, "SEMILLERO"),
    ("Consolidado", 3, 10, "SEMILLERO"),
    ("Destacado", 4, 15, "SEMILLERO"),
    ("Referente", 5, 20, "SEMILLERO"),
]

# (nombre, descripcion, tipo, grado, xp_requerido)
INSIGNIAS = [
    # ---- ESTUDIANTE · BRONCE
    ("Primer Paso", "Tiene su primer logro aprobado", "ESTUDIANTE", "BRONCE", 50),
    ("Voz Propia", "Hace su primera publicación académica", "ESTUDIANTE", "BRONCE", 100),
    ("Presente", "Participa en 1 evento", "ESTUDIANTE", "BRONCE", 150),
    ("Colaborador", "Tiene 3 logros aprobados", "ESTUDIANTE", "BRONCE", 250),
    ("Conectado", "Recibe 10 reacciones en sus publicaciones", "ESTUDIANTE", "BRONCE", 350),
    # ---- ESTUDIANTE · PLATA
    ("Participante Constante", "Participa en 3 eventos", "ESTUDIANTE", "PLATA", 450),
    ("Investigador Productivo", "Tiene 5 logros aprobados", "ESTUDIANTE", "PLATA", 600),
    ("Divulgador", "Hace 10 publicaciones académicas", "ESTUDIANTE", "PLATA", 800),
    ("Ponente", "Tiene 1 logro tipo Ponencia aprobado", "ESTUDIANTE", "PLATA", 1000),
    ("Influyente", "Recibe 25 reacciones en sus publicaciones", "ESTUDIANTE", "PLATA", 1250),
    # ---- ESTUDIANTE · ORO
    ("Autor", "Tiene 1 artículo aprobado", "ESTUDIANTE", "ORO", 1500),
    ("Trabajo Destacado", "Tiene 3 logros entre artículos y ponencias", "ESTUDIANTE", "ORO", 1800),
    ("Proyecto Innovador", "Tiene 1 logro tipo Proyecto aprobado", "ESTUDIANTE", "ORO", 2100),
    ("Referente del Semillero", "Es el estudiante con más XP de su semillero", "ESTUDIANTE", "ORO", 2500),
    ("Embajador", "Participa en 10 eventos", "ESTUDIANTE", "ORO", 2900),
    # ---- ESTUDIANTE · PLATINO
    ("Inventor", "Tiene 1 patente aprobada", "ESTUDIANTE", "PLATINO", 3400),
    ("Investigador Integral", "Tiene al menos un logro de cada uno de los 5 tipos", "ESTUDIANTE", "PLATINO", 4000),
    ("Mentor de la Comunidad", "Recibe 100 reacciones en sus publicaciones", "ESTUDIANTE", "PLATINO", 4700),
    ("Excelencia Investigativa", "Tiene 35 logros aprobados", "ESTUDIANTE", "PLATINO", 5500),
    ("Leyenda RIUL", "Está en el Top 3 del ranking de estudiantes", "ESTUDIANTE", "PLATINO", 6500),
    # ---- SEMILLERO · BRONCE
    ("Nacimiento", "Tiene su primer logro aprobado", "SEMILLERO", "BRONCE", 150),
    ("Equipo Formado", "Llega a 5 miembros activos", "SEMILLERO", "BRONCE", 300),
    ("Primer Proyecto", "Registra su primer proyecto", "SEMILLERO", "BRONCE", 450),
    ("En Convocatoria", "Se inscribe a una convocatoria", "SEMILLERO", "BRONCE", 750),
    ("Presencia en Eventos", "Participa en 1 evento", "SEMILLERO", "BRONCE", 1050),
    # ---- SEMILLERO · PLATA
    ("Estudiantes Activos", "Al menos la mitad de sus miembros tiene un logro aprobado", "SEMILLERO", "PLATA", 1350),
    ("Buena Participación en Eventos", "La mayoría de sus miembros participa en 4 eventos", "SEMILLERO", "PLATA", 1800),
    ("Productividad Constante", "Suma 15 logros aprobados", "SEMILLERO", "PLATA", 2400),
    ("Voz del Semillero", "Hace 10 publicaciones académicas", "SEMILLERO", "PLATA", 3000),
    ("Avance Sostenido", "Un proyecto suyo llega a 5 avances registrados", "SEMILLERO", "PLATA", 3750),
    # ---- SEMILLERO · ORO
    ("Semillero Destacado", "Suma 3 logros entre artículos y ponencias", "SEMILLERO", "ORO", 4500),
    ("Proyecto Innovador", "Tiene 1 logro tipo Proyecto aprobado", "SEMILLERO", "ORO", 5400),
    ("Cantera de Talento", "Llega a 10 miembros activos", "SEMILLERO", "ORO", 6300),
    ("Convocatorias Recurrentes", "Se inscribe a 3 convocatorias", "SEMILLERO", "ORO", 7500),
    ("Embajador", "Participa en 10 eventos", "SEMILLERO", "ORO", 8700),
    # ---- SEMILLERO · PLATINO
    ("Patente del Semillero", "Tiene 1 patente aprobada", "SEMILLERO", "PLATINO", 10200),
    ("Semillero Integral", "Tiene logros de los 5 tipos", "SEMILLERO", "PLATINO", 12000),
    ("Alto Impacto", "Suma 200 reacciones en sus publicaciones", "SEMILLERO", "PLATINO", 14100),
    ("Excelencia Colectiva", "Suma 100 logros aprobados", "SEMILLERO", "PLATINO", 16500),
    ("Referente RIUL", "Está en el Top 3 del ranking de semilleros", "SEMILLERO", "PLATINO", 19500),
]


def cargar(conexion):
    """Inserta lo que falte. Devuelve cuántos registros nuevos creó por tabla."""
    nuevos = {"tipologro": 0, "nivel": 0, "insignia": 0}

    for nombre, xp, limite in TIPOS_LOGRO:
        existe = conexion.execute(
            text("SELECT 1 FROM tipologro WHERE nombre = :n"), {"n": nombre}
        ).first()
        if existe:
            conexion.execute(
                text("UPDATE tipologro SET xp_otorgado = :x, limite_semanal = :l "
                     "WHERE nombre = :n"),
                {"n": nombre, "x": xp, "l": limite},
            )
        else:
            conexion.execute(
                text("INSERT INTO tipologro (nombre, xp_otorgado, limite_semanal) "
                     "VALUES (:n, :x, :l)"),
                {"n": nombre, "x": xp, "l": limite},
            )
            nuevos["tipologro"] += 1

    for nombre, estrellas, minimas, tipo in NIVELES:
        existe = conexion.execute(
            text("SELECT 1 FROM nivel WHERE nombre = :n AND tipo = :t"),
            {"n": nombre, "t": tipo},
        ).first()
        if not existe:
            conexion.execute(
                text("INSERT INTO nivel (nombre, estrellas, insignias_minimas, tipo) "
                     "VALUES (:n, :e, :m, :t)"),
                {"n": nombre, "e": estrellas, "m": minimas, "t": tipo},
            )
            nuevos["nivel"] += 1

    for nombre, descripcion, tipo, grado, xp in INSIGNIAS:
        existe = conexion.execute(
            text("SELECT 1 FROM insignia WHERE nombre = :n AND tipo = :t"),
            {"n": nombre, "t": tipo},
        ).first()
        if not existe:
            conexion.execute(
                text("INSERT INTO insignia (nombre, descripcion, tipo, grado, xp_requerido) "
                     "VALUES (:n, :d, :t, :g, :x)"),
                {"n": nombre, "d": descripcion, "t": tipo, "g": grado, "x": xp},
            )
            nuevos["insignia"] += 1

    return nuevos


if __name__ == "__main__":
    from app import create_app
    from app.extensions import db

    app = create_app()
    with app.app_context():
        resultado = cargar(db.session)
        db.session.commit()
        print("Registros nuevos:", resultado)
        for tabla in ("tipologro", "nivel", "insignia"):
            total = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
            print(f"Total en {tabla}: {total}")
import os
from datetime import timedelta

class config:
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://inventory_user:inventory_password@db:3306/inventory_db"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "clave-secreta-riul"
    )
    
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "suero-clave-secret"
    )
    
    # La sesión expira a los 10 minutos sin actividad 
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

    SESSION_REFRESH_EACH_REQUEST = True
   
    #3600 segundos = 1 hora
    JWT_ACCESS_TOKEN_EXPIRES = 3600
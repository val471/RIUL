import os

class config:
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://inventory_user:inventory_password@db:3306/inventory_db"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY",
        "suero-clave-secret"
    )
    #3600 segundos = 1 hora
    JWT_ACCESS_TOKEN_EXPIRES = 3600
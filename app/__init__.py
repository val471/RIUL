from flask import Flask
from flask_jwt_extended import JWTManager

#importamos las configuraciones

#manejo de las rutas con el blueprint

def create_app() :
    app = Flask(
        __name__
        static_folder="static"
        template_folder="templates"
    )

#Cargamos las configuraciones

#app.config.from.objetc(config)

#inicializamos la bd con app

#inicializamos JWT

#Registramos las rutas

#API auth

with app.app_context():
    #inicializamos los modelos

    #creamos la base de datos

    return app
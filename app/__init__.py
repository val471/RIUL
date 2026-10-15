from flask import Flask
from flask_jwt_extended import JWTManager

#importamos las configuraciones
from app.config import config
from app.extensions import db

#manejo de las rutas con el blueprint


def create_app() :
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
        
        
    )

#Cargamos las configuraciones

#
    app.config.from_object(config)

#inicializamos la bd con app
    db.init_app(app)
#inicializamos JWT
    JWTManager(app)
# Registramos las rutas web
    from app.routes.web import web
    app.register_blueprint(web)

#API auth

    with app.app_context(): 
        #inicializamos los modelos

        #creamos la base de datos

        return app
from flask import Flask
from app.routes import all_blueprints
from app.extensions import db ,migrate,jwt,bcrypt,cors
from app import models

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    # Initialize CORS (configurable allowed origins)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Register routes (blueprints)
    for bp in all_blueprints:
        app.register_blueprint(bp)  

    return app


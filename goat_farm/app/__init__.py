from flask import Flask
from app.routes import all_blueprints
from app.extensions import db ,migrate

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so they are registered with SQLAlchemy
    from app import models

    # Register routes (blueprints)
    for bp in all_blueprints:
        app.register_blueprint(bp)  

    with app.app_context():
        db.create_all()

    return app


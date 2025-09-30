from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# initialize db
db = SQLAlchemy()

def create_app(config_class="app.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from app import models

    # Register routes (blueprints)
    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app


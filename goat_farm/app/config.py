import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://gideon:123password@localhost/goatfarm"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    """Configuration for testing."""
    # This flag enables testing mode in Flask extensions
    TESTING = True 
    # This tells SQLAlchemy to use a temporary database in RAM
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # You can also disable CSRF protection for tests if you use Flask-WTF
    WTF_CSRF_ENABLED = False
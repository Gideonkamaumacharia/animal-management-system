import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://gideon:123password@localhost/goatfarm"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

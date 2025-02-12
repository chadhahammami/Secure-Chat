import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '8a24a6c38dba36f1a9ed7365cf80d39e'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

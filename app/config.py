import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRATION_MINUTES = 1400
    HISTORY_TOKEN_EXPIRATION_MINUTES = 120
    PROJECT_ID = 'e3fsf34fdf'
    BUCKET_NAME = 'dvfeeec'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

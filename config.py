from os import environ
from datetime import timedelta
from flask_jwt_extended import JWTManager
class Config:
    """Base config"""
    FLASK_APP = environ.get('FLASK_APP')
    ENVIRONMENT = environ.get('ENVIRONMENT')
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=int(environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS')))

class DevelopmentConfig(Config):
    """Development config"""
    SECRET_KEY = environ.get('DEVELOPMENT_SECRET_KEY')
    TESTING = True
    SQLALCHEMY_DATABASE_URI= environ.get('DEVELOPMENT_DATABASE_URI')
    JWT_SECRET_KEY = environ.get('DEVELOPMENT_JWT_SECRET_KEY')


class ProductionConfig(Config):
    """Production config"""
    JWT_SECRET_KEY = environ.get('PRODUCTION_JWT_SECRET_KEY')
    SECRET_KEY = environ.get('PRODUCTION_SECRET_KEY')
    TESTING = False
    SQLALCHEMY_DATABASE_URI= environ.get('PRODUCTION_DATABASE_URI')
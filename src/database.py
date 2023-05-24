from flask_pymongo import PyMongo
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager



db = PyMongo()
ma = Marshmallow()
migrate = Migrate()
jwt = JWTManager()
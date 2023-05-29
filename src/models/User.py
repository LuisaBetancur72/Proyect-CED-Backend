from datetime import datetime
from src.database import db,ma
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.orm import validates
from sqlalchemy import event, Boolean
from sqlalchemy.sql.expression import false
import re
from enum import Enum

from .message import Message

class User(db.Model):
    id            =db.Column(db.Integer, primary_key= True, autoincrement=True)
    type_user     = db.Column(db.String(50), nullable=False)
    email         =db.Column(db.String(60), unique=True, nullable =False)
    fullname      =db.Column(db.String(50), nullable=False)
    password      =db.Column(db.String(150), unique= True, nullable=False)
    phone         =db.Column(db.String(11), nullable=False)
    active        =db.Column(Boolean, nullable=False, server_default=false())
    Departamento  =db.Column(db.String(30), nullable=False)
    Municipio     =db.Column(db.String(30), nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.now())
    updated_at    = db.Column(db.DateTime, onupdate=datetime.now())

    messages = db.relationship('Message',backref="owner")
    
    def __init__(self, **fields):
        super().__init__(**fields)
        self.active = False

    def __setattr__(self, name, value):
        if(name == "password"):
            value = User.hash_password(value)

        super(User,self).__setattr__(name, value)

    @staticmethod
    def hash_password(password):
        if not password:
            raise AssertionError('Password not provided')
    
    #    if not re.match('\d.*[A-Z]|[A-Z].*\d', password):
    #       raise AssertionError('Password must contain 1 capital letter and 1 number')

    #    if len(password) < 7 or len(password) > 50:
    #        raise AssertionError('Password must be between 7 and 50 characters')
        return generate_password_hash(password)


    def check_password(self,password):
        return check_password_hash(self.password,password)
    
    @validates(type_user)
    def validate_nombre(self, value):
        if not value:
            raise AssertionError('No name provided')
        if not value.isalnum():
            raise AssertionError('Name value must be alphanumeric')
        if len(value) < 5 or len(value) > 80:
            raise AssertionError('Name must be between 5 and 80 characters')

        return value
        
    
    @validates('email')
    def validate_email(self, key, value):
        if not value:
            raise AssertionError('Email not provided')
        if not re.match("[^@]+@[^@]+\.[^@]+", value):
            raise AssertionError('Provided email is not a valid email address')
        if not value.endswith('@autonoma.com'):
            raise AssertionError('Email domain must be @autonoma.com')
        if User.query.filter(User.email == value).first():
            raise AssertionError('Email is already in use')
        return value
    
    @validates(fullname)
    def validate_nombre(self, value):
        if not value:
            raise AssertionError('No name provided')
        if not value.isalnum():
            raise AssertionError('Name value must be alphanumeric')
        if len(value) < 5 or len(value) > 80:
            raise AssertionError('Name must be between 5 and 80 characters')

        return value
    
    @validates(phone)
    def validate_phone(self,value):
        if not value:
            raise AssertionError('No phone number provided')
        if not re.match("^\+?\d{1,3}\s*\(?\d{3}\)?\s*\d{3}\s*\-?\s*\d{4}$",value):
            raise ArithmeticError('Phone is not correct')
        if len(value) <10 or len (value) >15:
            raise AssertionError('lastname must be between 10 and 15 characters')
    
        return value

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        #fields = ()
        model = User
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)

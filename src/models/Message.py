from datetime import datetime
from src.database import db,ma 
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.orm import validates
import re


class User(db.Model):
    email     =db.Column(db.String(60), primary_ket =True, nullable =False)
    fullname  =db.Column(db.String(80), nullable=False)
    password  =db.Column(db.String(50), unique= True, nullable=False)
    phone     =db.Column(db.String(11), nullable=False)
    
def __init__(self, **fields):
    super().__init__(**fields)


    def __setattr__(self, name, value):
        if(name == "password"):
            value = User.hash_password(value)

        super(User,self).__setattr__(name, value)

    @staticmethod
    def has_password(password):
        if not password:
            raise AssertionError('Password not provided')
        return generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password,password)
    
    @validates
    def validate_email(self,key,value):
        if  not value
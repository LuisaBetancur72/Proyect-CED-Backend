from datetime import datetime
from src.database import db,ma 
from sqlalchemy.orm import validates
import re

class Message(db.Model):
    id            =db.Column(db.Integer, primary_key= True, autoincrement=True)
    addressee     =db.Column(db.String(25), nullable=False)
    type_message  =db.Column(db.String(25), nullable=False)
    description   =db.Column(db.String(50), nullable=False)
    created_at    =db.Column(db.DateTime, default=datetime.now())
    updated_at    =db.Column(db.DateTime, onupdate=datetime.now())
    creator_user  =db.Column(db.String(25),db.ForeignKey('user.email',onupdate="CASCADE",ondelete="RESTRICT"),nullable=False)
    
    def __init__(self, **fields):
        super().__init__(**fields)

    def __repr__(self) -> str:
        return f"User >>> {self.name}"

    @validates("id")
    def validate_id(self,value):
        if not value:
            raise AssertionError('No id provided')
        if not value.isalnum():
            raise AssertionError('Id value must be alphanumeric')
        if Message.query.filter(Message.id == value).first():
            raise AssertionError('Id is already in use')

        return value
    
    
    @validates("description")
    def validate_name(self, key, value):
        if not value:
            raise AssertionError('No description provided')
        if not value.isalnum():
            raise AssertionError('description value must be alphanumeric')
        if len(value) < 5 or len(value) > 50:
            raise AssertionError('description must be between 5 and 100 characters')

        return value
        
    @validates("type_message")
    def validate_name(self, key, value):
        if not value:
            raise AssertionError('No type_message provided')
        if not value.isalnum():
            raise AssertionError('type_message value must be alphanumeric')
        if len(value) < 5 or len(value) > 25:
            raise AssertionError('type_message must be between 5 and 100 characters')

        return value
    
    @validates("addressee")
    def validate_email(self, key, value):
        if not value:
            raise AssertionError('addressee not provided')
        if not re.match("[^@]+@[^@]+\.[^@]+", value):
            raise AssertionError('Provided email is not a valid addressee address')
        if not value.endswith('@autonoma.com'):
            raise AssertionError('addressee domain must be @autonoma.com')
        if Message.query.filter(Message.addressee == value).first():
            raise AssertionError('addressee is already in use')
        return value
    
class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model=Message
        include_fk=True

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
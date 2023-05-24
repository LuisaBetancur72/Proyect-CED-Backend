from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.message import Message, message_schema, messages_schema

messages = Blueprint("messages",__name__,url_prefix="/api/v1/user/messages")

@messages.get("/")

def read_all():
    current_user_id = get_jwt_identity()  
    messages = Message.query.filter_by(creator_user=current_user_id).first()
      
    messages = Message.query.order_by(Message.id).all()
    return {"data": messages_schema.dump(messages)}, HTTPStatus.OK

@messages.get("/<int:id>")
@jwt_required()
def read_one(id):
    current_user_id = get_jwt_identity()
    
    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()

    if (not message):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": messages_schema.dump(message)}, HTTPStatus.OK

@messages.post("/")
@jwt_required()
def create():
    current_user_id = get_jwt_identity()
    
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST
    date_request = request.get_json().get("date", None)
    date_m = datetime.strptime(date_request, '%Y-%m-%d').date()


    message = Message(
        date=date_m,
        addressee=request.get_json().get("addressee", None),
        type_message=request.get_json().get("type_message", None),
        description=request.get_json().get("description", None),
        creator_user=current_user_id
        )

    try:
        db.session.add(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.CREATED

@messages.put("/<int:id>")
@jwt_required()
def update(id):
    current_user_id=get_jwt_identity()
    
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    data_request = request.get_json().get("fecha", None)
    date_m = datetime.strptime(data_request, '%Y-%m-%d').date()


    message.date = date_m,
    message.addressee = request.get_json().get("addressee", message.addressee)
    message.type_message = request.get_json().get("type_message", message.type_message)
    message.description = request.get_json().get("description", message.description)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST
    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@messages.delete("/<int:id>")
@jwt_required()
def delete(id):
    current_user_id=get_jwt_identity()
    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()
    
    if not messages:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.NO_CONTENT

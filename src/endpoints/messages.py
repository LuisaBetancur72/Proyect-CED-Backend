from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from flask_jwt_extended import jwt_required

from src.models.message import Message, message_schema, messages_schema

messages = Blueprint("messages",__name__,url_prefix="/api/v1/messages")

@messages.get("/")
def read_all():
    messages = Message.query.order_by(Message.id).all()
    return {"data": messages_schema.dump(messages)}, HTTPStatus.OK

@messages.get("/user/<int:id>")
@jwt_required()
def read_one(id):
    
    message = Message.query.filter_by(id=id).all()

    if (not message):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": messages_schema.dump(message)}, HTTPStatus.OK

@messages.post("/")
def create():
    post_data = None
    
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST
    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()


    message = Message(date=request.get_json().get("date", None),
        addressee=request.get_json().get("addressee", None),
        type_message=request.get_json().get("type_message", None),
        description=request.get_json().get("description", None),
        creator_user=request.get_json().get("creator_user", None))

    try:
        db.session.add(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.CREATED

@messages.put("/id")
@jwt_required()
def update(id):
    
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message.query.filter_by(id=id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()


    message.date = request.get_json().get("date", message.date)
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
    message = Message.query.filter_by(id=id).first()

    if not messages:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.NO_CONTENT


@messages.get("/user/<int:creator_user>/fecha")
@jwt_required()
def read_by_date_range(creator_user):
    date = None
    try:
        date = request.get_json()
    
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Get body JSON data not found", 
                "message": str(e)}, HTTPStatus.BAD_REQUEST
    
    fecha_request_i = request.get_json().get("fecha_inicio", None)
    fecha_request_f = request.get_json().get("fecha_fin", None)  
        
    fecha_inicio = datetime.strptime(fecha_request_i, '%Y-%m-%d').date()
    fecha_fin    = datetime.strptime(fecha_request_f, '%Y-%m-%d').date()

    messages = Message.query.filter_by(creator_user=creator_user).filter(Message.fecha >= fecha_inicio, Message.fecha <= fecha_fin).all()
        
    return {"data": messages_schema.dump(messages)}, HTTPStatus.OK
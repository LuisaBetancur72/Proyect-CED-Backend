from flask import Blueprint, request
from http import HTTPStatus
import werkzeug
from datetime import datetime
import sqlalchemy.exc
from src.database import db,ma
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.message import Message, message_schema, messages_schema

message = Blueprint("message", __name__, url_prefix="/api/v1/message")

@message.get("/")
def read_all():
    messages = Message.query.order_by(Message.id).all()
    return {"data": messages_schema.dump(messages)}, HTTPStatus.OK

@message.get("/user/<int:id>")
@jwt_required()
def read_one(id):
    current_user_id = get_jwt_identity()
    
    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@message.post("/")
@jwt_required()
def create():
    current_user_id = get_jwt_identity()

    post_data = None
    
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message(
        id=request.get_json().get("id", None),
        date=request.get_json().get("date", None),
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

@message.put("/<int:id>")
@jwt_required()
def update(id):
    current_user_id = get_jwt_identity()
    
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    message.id = request.get_json().get("id", message.id)
    message.date = request.get_json().get("date", message.date)
    message.addressee = request.get_json().get("addressee", message.addressee)
    message.type_message = request.get_json().get("type_message", message.type_message)
    message.description = request.get_json().get("description", message.description)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@message.delete("/<int:id>")
@jwt_required()
def delete(id):
    current_user_id = get_jwt_identity()
    
    message = Message.query.filter_by(id=id, creator_user=current_user_id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.OK


@message.get("/date/<int:cedula>/")
@jwt_required()
def read_by_date_range(cedula):
    fecha = None
    try:
        fecha = request.get_json()
    
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Get body JSON data not found", 
                "message": str(e)}, HTTPStatus.BAD_REQUEST
    
    fecha_request_i = request.get_json().get("fecha_inicio", None)
    fecha_request_f = request.get_json().get("fecha_fin", None)  
        
    fecha_inicio = datetime.strptime(fecha_request_i, '%Y-%m-%d').date()
    fecha_fin    = datetime.strptime(fecha_request_f, '%Y-%m-%d').date()

    message = Message.query.filter_by(cedula=cedula).filter(Message.fecha >= fecha_inicio, Message.fecha <= fecha_fin).all()
        
    return {"data": messages_schema.dump(message)}, HTTPStatus.OK
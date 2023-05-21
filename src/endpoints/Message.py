from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime

from flask_jwt_extended import jwt_required

from src.models.Message import Message, message_schema, messages_schema

message = Blueprint("message",__name__,url_prefix="/api/v1/ingresos")

@message.get("/")
def read_all():
    message = message.query.order_by(message.id).all()
    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@message.get("/message/<int:id>")
@jwt_required()
def read_one(id):
    
    ingreso = Message.query.filter_by(id=id).all()

    if (not message):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@message.post("/")
def create():
    post_data = None
    
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST
    fecha_request = request.get_json().get("fecha", None)
    fecha_date = datetime.strptime(fecha_request, '%Y-%m-%d').date()


    message = Message(
                    id=request.get_json().get("id", None),
                    date=fecha_date,
                    addressee=request.get_json().get("addressee", None),
                    type_message=request.get_json().get("type_message", None))
                    
    try:
        db.session.add(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.CREATED

@message.put("/id")
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


    message.id = request.get_json().get("id", message.id)
    message.date = fecha_date
    message.addressee = request.get_jeson().get("addressee", message.addressee),
    message.type_message = request.get_json().get("type", message.type_message)
    
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST
    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@message.delete("/<int:id>")
@jwt_required()
def delete(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.NO_CONTENT



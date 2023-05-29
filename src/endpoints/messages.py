from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug
from datetime import datetime
from flask_cors import cross_origin,CORS

from flask_jwt_extended import jwt_required, get_jwt_identity

from src.models.user import User, users_schema, user_schema
from src.models.message import Message, message_schema, messages_schema

messages = Blueprint("messages",__name__)
CORS(messages)

@messages.route('/api/v1/user/messages/all', methods=['GET'])
@cross_origin()
def read_all():
    messages = Message.query.order_by(Message.id).all()
    return messages_schema.dump(messages), HTTPStatus.OK

@messages.route('/api/v1/messages/<int:id>', methods=['GET'])
@cross_origin()
def read_user_id(id):
    message = Message.query.filter_by(id=id).first()
    if not message:
        return {"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND

    return {"data": message_schema.dump(message)}, HTTPStatus.OK


@messages.get("/<int:id>")
@jwt_required()
def read_one(id):
    current_user_id = get_jwt_identity()
    creator_user =current_user_id["id"]
    
    message = Message.query.filter_by(id=id, creator_user=creator_user).first()

    if (not message):
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data": message_schema.dump(message)}, HTTPStatus.OK

@messages.route('/api/v1/mensajes/redactar', methods=['POST', 'OPTIONS'])
@cross_origin()
def create():
    if request.method == 'OPTIONS':
        # Manejar la solicitud OPTIONS sin procesarla en el resto del código
        return "", HTTPStatus.OK

    
    creator_user = 'luisa@autonoma.com'

    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message(
        addressee=post_data.get("addressee", None),
        type_message=post_data.get("type_message", None),
        description=post_data.get("description", None),
        creator_user=creator_user
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
    current_user_id = get_jwt_identity()
    creator_user = current_user_id["id"]
    
    post_data = None

    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    message = Message.query.filter_by(id=id, creator_user=creator_user).first()

    if not message:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND
    message.addressee = post_data.get("addressee", None)
    message.type_message = post_data.get("type_message", message.type_message)
    message.description = post_data.get("description", message.description)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)},HTTPStatus.OK

@messages.delete("/<int:id>")
@jwt_required()
def delete(id):
    current_user_id=get_jwt_identity()
    creator_user = current_user_id["id"]
    message = Message.query.filter_by(id=id, creator_user=creator_user).first()
    
    if not messages:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(message)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": message_schema.dump(message)}, HTTPStatus.NO_CONTENT

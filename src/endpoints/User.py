from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db, ma
import werkzeug

from src.models.user import User, user_schema, users_schema
from src.models.message import Message, message_schema, messages_schema
from flask_jwt_extended import jwt_required, get_jwt_identity


users = Blueprint("users", __name__, url_prefix="/api/v1/users")

@users.get("/")
@jwt_required()
def read_all():
    users = User.query.order_by(User.email).all()
    return {"data": users_schema.dump(users)}, HTTPStatus.OK

@users.get("/<int:id>")
@jwt_required()
def read_user(email):
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    current_user_id = get_jwt_identity()

    if current_user_id != user.email:
        return {"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED

    return {"data": user_schema.dump(user)}, HTTPStatus.OK

@users.post("/")
@jwt_required()
def create():
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    user = User(
        id=request.json.get("id", None),
        fullname=request.json.get("apellido", None),
        email=request.json.get("email", None),
        password=request.json.get("password", None),
        phone=request.json.get("phone", None)
    )

    current_user_id = get_jwt_identity()

    if current_user_id != user.id:
        return {"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED

    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": user_schema.dump(user)}, HTTPStatus.CREATED

@users.put('/<int:id>')
@jwt_required()
def update(email):
    post_data = None

    try:
        post_data = request.get_json()

    except werkzeug.exceptions.BadRequest as e:
        return {"error": "Post body JSON data not found", "message": str(e)}, HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "Resource not found"}, HTTPStatus.NOT_FOUND

    current_user_id = get_jwt_identity()

    if current_user_id != user.email:
        return {"error": "Unauthorized"}, HTTPStatus.UNAUTHORIZED

    user.fullname = request.json.get("fullname", user.fullname)
    user.email = request.json.get("email", user.email)
    user.password = request.json.get("password", user.password)
    user.phone = request.json.get("phone", user.phone)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Invalid resource values", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": user_schema.dump(user)}, HTTPStatus.OK

@users.delete("/<int:id>")
@jwt_required()
def delete(email):
    current_user_id = get_jwt_identity()
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND

    if current_user_id != user.email:
        return {"error": "No autorizado"}, HTTPStatus.UNAUTHORIZED

    try:
        db.session.delete(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error": "Valores inválidos para el recurso", "message": str(e)}, HTTPStatus.BAD_REQUEST

    return {"data": user_schema.dump(user)}, HTTPStatus.OK


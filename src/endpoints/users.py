from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db,ma
import werkzeug
from src.models.user import User, user_schema, users_schema
from src.models.message import Message, message_schema,messages_schema
from flask_cors import cross_origin,CORS


from flask_jwt_extended import jwt_required,get_jwt_identity

users = Blueprint("users",__name__)
CORS(users)

@users.get("/all")
def read_all():
 users = User.query.order_by(User.id).all()
 return {"data": users_schema.dump(users)}, HTTPStatus.OK


@users.get("/")
@jwt_required()
def read_user():
    current_user_id=get_jwt_identity()
    user_id=current_user_id["id"]
    user = User.query.filter_by(id=user_id).first()
    if(not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data":user_schema.dump(user)},HTTPStatus.OK

@users.route('/api/v1/users', methods=['POST', 'OPTIONS'])
@cross_origin()
def create():
    
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Posr body JSON data not found","message":str(e)},HTTPStatus.BAD_REQUEST

    user = User(
        fullname=request.json.get("fullname", None),
        email=request.json.get("email", None),
        password=request.json.get("password", None),
        phone=request.json.get("phone", None)
    )
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.CREATED


@users.put('/update')
@jwt_required()
def update():
    current_user_id=get_jwt_identity()
    email= current_user_id["email"]
    post_data=None

    try:
        post_data=request.get_json()

    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Post body JSON data not found",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    user=User.query.filter_by(email=email).first()

    if(not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    user.fullname = request.json.get("fullname", user.fullname)
    user.email = request.json.get("email", user.email)
    user.password = request.json.get("password", user.password)
    user.phone = request.json.get("phone", user.phone)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)}, HTTPStatus.OK

@users.delete("/eliminar")
@jwt_required()
def delete():
    current_user_id=get_jwt_identity()
    user_id= current_user_id["id"]
    
    user = User.query.filter_by(id=user_id).first()
    if (not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.NO_CONTENT

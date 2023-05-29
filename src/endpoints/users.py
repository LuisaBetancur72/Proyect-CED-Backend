from flask import Blueprint, request
from http import HTTPStatus
import sqlalchemy.exc
from src.database import db,ma
import werkzeug
from werkzeug.exceptions import BadRequest
from src.models.user import User, user_schema, users_schema
from src.models.message import Message, message_schema,messages_schema
from flask_cors import cross_origin,CORS
from sqlalchemy import Boolean


from flask_jwt_extended import jwt_required,get_jwt_identity

users = Blueprint("users",__name__)
CORS(users)

@users.route('/api/v1/users/all', methods=['GET'])
@cross_origin()
def read_all():
    users = User.query.order_by(User.id).all()
    return users_schema.dump(users), HTTPStatus.OK

@users.route('/api/v1/users/<int:user_id>', methods=['GET'])
@cross_origin()
def read_user_id(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return {"error": "Recurso no encontrado"}, HTTPStatus.NOT_FOUND

    return {"data": user_schema.dump(user)}, HTTPStatus.OK

@users.route('/api/v1/me/', methods=['GET'])
@cross_origin()
@jwt_required()
def read_user():
    current_user_id=get_jwt_identity()
    user_id=current_user_id["id"]
    user = User.query.filter_by(id=user_id).first()
    if(not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    return {"data":user_schema.dump(user)},HTTPStatus.OK

@users.route('/api/v1/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def create():
    
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Posr body JSON data not found","message":str(e)},HTTPStatus.BAD_REQUEST

    user = User(
        type_user=request.json.get("type_user", None),
        fullname=request.json.get("fullname", None),
        email=request.json.get("email", None),
        password=request.json.get("password", None),
        phone=request.json.get("phone", None),
        active=False,  # Set active to False
        Departamento=request.json.get("Departamento", None),
        Municipio=request.json.get("municipio", None)
    )
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.CREATED

@users.route('/api/v1/users/create', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_user():
    
    post_data = None
    try:
        post_data = request.get_json()
    except werkzeug.exceptions.BadRequest as e:
        return {"error":"Posr body JSON data not found","message":str(e)},HTTPStatus.BAD_REQUEST

    user = User(
        type_user=request.json.get("type_user", None),
        fullname=request.json.get("fullname", None),
        email=request.json.get("email", None),
        password=request.json.get("password", None),
        phone=request.json.get("phone", None),
        active=request.json.get('active'),  # Set active to False
        Departamento=request.json.get("Departamento", None),
        Municipio=request.json.get("municipio", None)
    )
    try:
        db.session.add(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.CREATED



@users.route('/api/v1/users/update/<int:user_id>', methods=['PUT', 'GET'])
@cross_origin()
def update(user_id):
    if request.method == 'PUT':
        post_data = None

        try:
            post_data = request.get_json()
        except BadRequest as e:
            return {
                "error": "Post body JSON data not found",
                "message": str(e)
            }, HTTPStatus.BAD_REQUEST

        user = User.query.filter_by(id=user_id).first()

        if not user:
            return {
                "error": "Resource not found"
            }, HTTPStatus.NOT_FOUND

        user.fullname = post_data.get("fullname", user.fullname)
        user.email = post_data.get("email", user.email)
        user.password = post_data.get("password", user.password)
        user.phone = post_data.get("phone", user.phone)
        user.active = post_data.get("active", user.active)
        user.Departamento = post_data.get("Departamento", user.Departamento)
        user.Municipio = post_data.get("municipio", user.Municipio)
        user.active = bool(post_data.get('active'))
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            return {
                "error": "Invalid resource values",
                "message": str(e)
            }, HTTPStatus.BAD_REQUEST

        return {
            "data": user_schema.dump(user)
        }, HTTPStatus.OK

    elif request.method == 'GET':
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return {
                "error": "Resource not found"
            }, HTTPStatus.NOT_FOUND

        return {
            "data": user_schema.dump(user)
        }, HTTPStatus.OK

    return {
        "error": "Method not allowed"
    }, HTTPStatus.METHOD_NOT_ALLOWED

@users.route('/api/v1/', methods=['PUT'])
@cross_origin()
@jwt_required()
def edit_me():
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
    user.active = request.json.get("acive", False)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
               return {"error":"Invalid resource values",
                "message":str(e)}, HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.OK


@users.route('/api/v1/users/delete/<int:user_id>', methods=['DELETE'])
@cross_origin()
def delete(user_id):
   
    user = User.query.filter_by(id=user_id).first()
    if (not user):
        return {"error":"Resource not found"}, HTTPStatus.NOT_FOUND

    try:
        db.session.delete(user)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as e:
        return {"error":"Invalid resource values","message":str(e)},HTTPStatus.BAD_REQUEST

    return {"data":user_schema.dump(user)},HTTPStatus.NO_CONTENT
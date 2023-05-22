from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user
from http import HTTPStatus
from src.database import jwt

from src.models.User import User, user_schema, users_schema 

auth = Blueprint("auth",
                __name__,
                url_prefix="/api/v1/auth")


@auth.post("/login")
def login():
    fullname = request.get_json().get("fullname", None)
    password = request.get_json().get("password", None)

    user = User.query.filter_by(cedula=fullname).one_or_none()
    
    if not user or not user.check_password(password):
        return {"error": "Wrong username or password"}, HTTPStatus.UNAUTHORIZED 
    
    access_token = create_access_token(identity=user_schema.dump(user)) 
    response = {"access_token": access_token} 

    return response, HTTPStatus.OK 
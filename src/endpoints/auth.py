from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token,get_jwt_identity,get_jwt
from http import HTTPStatus
from src.database import jwt
from flask_cors import cross_origin, CORS
from datetime import datetime, timezone, timedelta

from src.models.user import User, user_schema, users_schema

auth = Blueprint("auth", __name__)
CORS(auth)


@auth.route("/api/v1/login", methods=['POST', 'OPTIONS'])
@cross_origin()
def create():
    username = request.get_json().get("username", None)
    password = request.get_json().get("password", None)

    user = User.query.filter_by(email=username).one_or_none()

    if not user or not user.check_password(password):
        return {"error": "Wrong username or password"}, HTTPStatus.UNAUTHORIZED

    access_token = create_access_token(identity=user_schema.dump(user))
    refresh_token = create_refresh_token(identity=user_schema.dump(user))
    
    if user.active != True and user.active != 1:
        return jsonify({'message': 'Usuario no activo'}),HTTPStatus.UNAUTHORIZED

    response = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

    return response, HTTPStatus.OK


@auth.route("/logout", methods=["POST"])
def logout():
    response = {"message": "logout successful"}
    # Clear cookies or perform any other necessary logout operations
    return response, HTTPStatus.OK


@auth.after_request
def refresh_access_token(response):
    try:
        user=get_jwt_identity()
        user_id=user["id"]
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=user_schema.dump(user_id))
            response.set_cookie("access_token_cookie", access_token)  # Set access token as a cookie
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

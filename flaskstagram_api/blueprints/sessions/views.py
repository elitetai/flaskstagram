from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.security import check_password_hash
from models.user import User

sessions_api_blueprint = Blueprint('sessions_api',
                                    __name__,
                                    template_folder='templates')

@sessions_api_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = User.get_or_none(User.username == username)
    if user: 
        checked_hashed = check_password_hash(user.hashed_password, password)
        if checked_hashed:
            token = create_access_token(identity=user.username)
            response = jsonify({
                "auth_token": token,
                "message": "Successfully logged in",
                "status": "Success",
                "user": {
                    "username": user.username,
                    "profileImage": user.full_image_path
                }
            })
        else:
            response = jsonify({
                "message": "Wrong password provided",
                "status": "Failed",
            }), 401
    else:
        response = jsonify({
            "message": "User not found",
            "status": "Failed",
        }), 404
    return response
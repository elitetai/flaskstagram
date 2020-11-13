from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models.user import User

users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder="templates")

@users_api_blueprint.route('/check_name', methods=['GET'])
def check_name():
    import re
    username = request.args.get('username')
    
    for user in User.select():
        result = re.search(username, user.username, re.IGNORECASE)
        if result:
            response = {
                "exists": True,
                "valid": False
            }
            break
    else:
        response = {
            "exists": False,
            "valid": True
        }
    return jsonify(response)
    
    
@users_api_blueprint.route('/signup', methods=['POST'])
def create():
    params = request.json
    new_user = User(username=params.get('username'), email=params.get('email'), password=params.get('password'))
    if new_user.save():
        token = create_access_token(identity=new_user.username)
        response = jsonify({
            "auth_token": token,
            "message": "Successfully signed up",
            "status": "Success",
            "user": {
                "id": new_user.id,
                "username": new_user.username
            }
        })
        return response
    else: 
        response = []
        for err in new_user.errors:
            response.append({
                "message": err,
                "status": "Failed"
            })
        return jsonify(response), 401
   

@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    username = get_jwt_identity()
    user = User.get_or_none(User.username == username)
    if user: 
        response = jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "profile_picture": user.full_image_path
        })
    else:
        response = jsonify({
            "message": "User not found",
            "status": "Failed"
        }), 404
    return response

@users_api_blueprint.route('/<username>', methods=['GET'])
@jwt_required
def show(username):
    current_user_username = get_jwt_identity()
    current_user = User.get_or_none(User.username == current_user_username)
    if current_user:
        user = User.get_or_none(User.username == username)
        if user:
            response = jsonify({
                "id": user.id,
                "username": user.username,
                "profileImage": user.full_image_path
            })
        else:
            response = jsonify({
                "message": f"{username} not found",
                "status": "Failed"
            }), 404
    else:
        response = 404, jsonify({
            "message": "User not found",
            "status": "Failed"
        })
    return response

@users_api_blueprint.route('/', methods=['GET'])
def index():
    response = []
    for i in User:
        response.append({ 
            "id": i.id,
            "username": i.username,
            "profileImage": i.full_image_path
        })
    return jsonify(response)

# @users_api_blueprint.route('/update', methods=['POST'])
# # @jwt_required
# def update():
#     # username = get_jwt_identity()
#     username = request.json.get('username')
#     user = User.get_or_none(User.username == username)
#     if user:         
#         email = request.json.get('email')
#         password = request.json.get('password')
#         private = request.json.get('private')

#         if len(password) > 0:
#             user.password = password
        
#         if (user.username != username) or (user.email != email) or (user.is_private != bool(private)) or password:
#             # Change is_private's status 
#             if user.is_private != bool(private):
#                 user.is_private = bool(private)

#             if user.save():
#                 token = create_access_token(identity=user.username)
#                 response = jsonify({
#                     "auth_token": token,
#                     "message": "User's details have successfully updated",
#                     "status": "Success",
#                     "user": {
#                         "id": user.id,
#                         "username": user.username
#                     }
#                 })
#             else:
#                 response = []
#                 for err in user.errors:
#                     response.append({
#                         "message": f"Unable To update! Error reason: {err}",
#                         "status": "Failed"
#                     })
#                 return jsonify(response), 401
#         else:
#             response = jsonify({
#                 "message": "No detail has been amended",
#                 "status": "Failed"
#             }), 404
#     else:
#         response = jsonify({
#             "message": "User not found",
#             "status": "Failed"
#         }), 404
#     return response
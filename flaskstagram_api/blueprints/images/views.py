from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from werkzeug.utils import secure_filename
from models.user import User
from models.image import Image
from models.like import Like
from flaskstagram_api.util.helpers import allowed_file, upload_file_to_s3

images_api_blueprint = Blueprint('images_api',
                                __name__,
                                template_folder='templates')

@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def show():
    username = get_jwt_identity()
    user = User.get_or_none(User.username==username)

    if user:
        response = []
        for image in user.sorted_images:
            response.append(image.full_image_url)
        return jsonify(response)
    else:
        response = {
            "message": "User not found",
            "status": "Failed"
        }
    return jsonify(response), 404  

@images_api_blueprint.route('/images', methods=['GET'])
def index():
    user_id = request.args.get('userId')
    user = User.get_or_none(User.id==user_id)
    if user: 
        response = []
        for image in user.sorted_images:
            response.append({
                "url": image.full_image_url,
                "id": image.id
            })
        return jsonify(response)
    else: 
        response = {
            "message": "User not found",
            "status": "Failed"
        }
    return jsonify(response), 404  

@images_api_blueprint.route('/', methods=['POST'])
@jwt_required
def upload():
    username = get_jwt_identity()
    user = User.get_or_none(User.username==username)
    if user:
        # If user submit an empty part without filename
        file = request.files["image"]
        if file.filename=="":
            return jsonify({
                "message": "Image not provided",
                "status": "Failed"
            }), 404

        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            image_path = upload_file_to_s3(file, user.username)
            # change path for either user's profile image or user's images  
            if request.form["path"]=='user':
                user.image_path = image_path
                if user.save():
                    response = jsonify({
                        "profile_picture": user.full_image_path,
                        "success": True
                    })
                else:
                    response = []
                    for err in user.errors:
                        response.append({
                            "message": err,
                            "status": "Failed"
                        })
                    return jsonify(response), 401
            else:
                image = Image(user=user, image_url=image_path)
                if image.save():
                    response = jsonify({
                        "image_url": image.full_image_url,
                        "success": True
                    })
                else:
                    response = jsonify({
                        "message": "Failed to save image",
                        "status": "Failed"
                    }), 401
        else: 
            response = jsonify({
                "message": "Wrong file type provided",
                "status": "Failed"
            }), 401
    else:
        response = jsonify({
            "message": "User not found",
            "status": "Failed"
        }), 404
    return response

@images_api_blueprint.route('/<id>/toggle_like', methods=['POST', 'GET'])
@jwt_required
def toggle_like(id):
    username = get_jwt_identity()
    user = User.get_or_none(User.username==username)
    if user: 
        image = Image.get_or_none(Image.id==id)
        check_like = Like.get_or_none(Like.fan==user, Like.image==image)
        if request.method=='GET':
            if check_like: 
                response = jsonify({
                    "total_likes": len(check_like.total_likes),
                    "image_id": image.id,
                    "liked": True
                }), 200
            else:
                response = jsonify({
                    "total_likes": None,
                    "image_id": image.id,
                    "liked": False
                }), 200
        else:
            if check_like: 
                similar_image = Like.get_or_none(Like.image==check_like.image)
                check_like.delete_instance()
                response = jsonify({
                    "total_likes": len(similar_image.total_likes),
                    "image_id": image.id,
                    "liked": False
                }), 200
            else: 
                new_like = Like(image=image, fan=user)
                new_like.save()
                response = jsonify({
                    "total_likes": len(new_like.total_likes),
                    "image_id": image.id,
                    "liked": True
                }), 200
    else:
        response = jsonify({
            "message": "User not found",
            "status": "Failed"
        }), 404
    return response
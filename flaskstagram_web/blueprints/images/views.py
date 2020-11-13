from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_required, current_user
from models.user import User
from models.image import Image
from werkzeug.utils import secure_filename
from flaskstagram_web.util.helpers import upload_file_to_s3, allowed_file

images_blueprint = Blueprint('images', 
                            __name__,
                            template_folder='templates')

@images_blueprint.route('/new', methods=['GET'])
@login_required
def new():
    return render_template('images/new.html')

@images_blueprint.route('/<image_id>/show', methods=['GET'])
@login_required
def show(image_id):
    image = Image.get_or_none(Image.id == image_id)
    return render_template('images/show.html', image=image)

@images_blueprint.route('/<id>/upload', methods=['POST'])
@login_required
def upload(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user.id == int(id):
            if "gallery_image" not in request.files:
                flash('wrong input name', 'danger')
                return redirect(url_for('images.new'))
            file = request.files['gallery_image']
            if file.filename == "":
                flash('Not found', 'danger')
                return redirect(url_for('images.    '))
            if file and allowed_file(file.filename):
                file.filename = secure_filename(file.filename)
                image_url = upload_file_to_s3(file, user.username)
                image = Image(user=user, image_url=image_url)
                if image.save():
                    return redirect(url_for('users.show', username=user.username))
            else: 
                flash("Wrong file type provided. Please try again", "danger")
                return redirect(url_for('images.new'))                
        else:
            flash("Not Allow To Upload Images Other Than Yourself!", "danger")
            return redirect(url_for('home'))
    else:
        flash("No user found!", "danger")
        return redirect(url_for('home'))


    
    
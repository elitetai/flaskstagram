from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from models.user import User
from flaskstagram_web.util.helpers import upload_file_to_s3, allowed_file

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('users/new.html')

@users_blueprint.route('/', methods=['POST'])
def create():
    params = request.form
    if params.get('private') == None: 
        new_user = User(username=params.get('username'), email=params.get('email'), password=params.get('password'))
    else:
        new_user = User(username=params.get('username'), email=params.get('email'), password=params.get('password'), is_private=True)
    if new_user.save():
        login_user(new_user)
        flash('Signup successful!', 'primary')
        return redirect(url_for('home'))
    else:
        for err in new_user.errors:
            flash(err, "danger")
        return redirect(url_for('users.new'))

@users_blueprint.route('/<username>', methods=['GET'])
@login_required
def show(username):
    
    user = User.get_or_none(User.username == username) 
    if user:
        fanidol = current_user.follow_status(user)
        return render_template('users/show.html', user=user, fanidol=fanidol)
    else:
        flash(f"User '{username}' is not found ", "danger")
        return redirect(url_for('home'))
    
# @users_blueprint.route('/', methods=['GET'])
# @login_required
# def index():
#     return 'USERS'

@users_blueprint.route('/<id>/edit', methods=['GET'])
@login_required
def edit(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user == user:   
            return render_template('users/edit.html', user=user)
        else:
            flash("Not Allow To Edit Users Other Than Yourself!", "danger")
            return redirect(url_for('home'))
    else:
        flash("No Such User!", "danger")
        return redirect(url_for('home'))

@users_blueprint.route('/<id>', methods=['POST'])
@login_required
def update(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user.id == int(id):
            user.username = request.form.get('username')
            user.email = request.form.get('email')
            password = request.form.get('password')
            private = request.form.get('private')

            # Check if password is not an empty string
            if len(password) > 0:
                user.password = password
            
            if (current_user.username != user.username) or (current_user.email != user.email) or (user.is_private != bool(private)) or password:
                # Change is_private's status 
                if user.is_private != bool(private):
                    user.is_private = bool(private)

                if user.save():
                    flash("User details have been successfully updated!", "primary")
                    return redirect(url_for('users.show', username=user.username))
                else:
                    for err in user.errors:
                        flash(err, "danger")
                    return redirect(url_for('users.edit', id=user.id))
            else:
                flash("No detail has been amended", "danger")  
                return redirect(url_for('users.edit', id=user.id))
        else:
            flash("Not Allow To Edit Users Other Than Yourself!", "danger")
            return redirect(url_for('users.show',username=user.username))
    else:
        flash("No Such User!", "danger")
        return redirect(url_for('home'))

@users_blueprint.route('/<id>/delete', methods=['POST'])
@login_required
def delete(id):
    user = User.get_or_none(User.id == id)
    if user.email == "admin@admin.com":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        targeted_user_username = User.get_or_none(User.username == username)
        targeted_user_email = User.get_or_none(User.email == email)
        if targeted_user_username == targeted_user_email:
            if check_password_hash(user.hashed_password, password):
                if targeted_user_username.delete_instance():
                    flash(f"User - {username} has successfully been deleted", "success")
                    return redirect(url_for('users.edit', id=user.id))
                else:
                    flash("Failed to delete user, please try again", "danger")
                    return redirect(url_for('users.edit', id=user.id))
            else:
                flash("Your password is incorrect. Please try again", "danger")
                return redirect(url_for('users.edit', id=user.id))
        else:
            flash("User and email are not the same", "danger")
            return redirect(url_for('users.edit', id=user.id))
    else:
        flash("Authorized personnel only!", "danger")
        return redirect(url_for('home'))

@users_blueprint.route('/<id>/upload', methods=['POST'])
@login_required
def upload(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user.id == int(id):
            if "profile_image" not in request.files:        
                flash("No file provided!", "danger")
                return redirect(url_for('users.edit', id=id))

            # If user submit an empty part without filename
            file = request.files["profile_image"]
            if file.filename == "":
                flash("No files provided! Please select a file", "danger")
                return redirect(url_for('users.edit', id=id))

            if file and allowed_file(file.filename):
                file.filename = secure_filename(file.filename)
                image_path = upload_file_to_s3(file, user.username)
                user.image_path = image_path
                if user.save():
                    return redirect(url_for("users.show",username=user.username))
                else:
                    for err in user.errors:
                        flash(err, "danger")
                    return redirect(url_for("users.edit", id=id))
            else: 
                flash("Wrong file type provided. Please try again", "danger")
                return redirect(url_for('users.edit', id=id))
        else:
            flash("Not Allow To Edit Users Other Than Yourself!", "danger")
            return redirect(url_for('users.show',username=user.username))
    else:
        flash("No Such User!")
        redirect(url_for("home")) 

@users_blueprint.route('/<idol_id>/follow', methods=['POST'])
@login_required
def follow(idol_id):
    idol = User.get_by_id(idol_id)

    if current_user.follow(idol):
        if current_user.follow_status(idol).is_approved:
            flash(f"You follow {idol.username}", "primary")
        else:
            flash(f"You send request to follow {idol.username}", "primary")
        return redirect(url_for('users.show', username=idol.username)) 
    else:
        flash("Unable to follow this user, try again", "danger")
        return redirect(url_for('users.show', username=idol.username))
        
@users_blueprint.route('/<id>/request', methods=['GET'])
@login_required
def show_request(id):
    user = User.get_or_none(User.id == id)
    if user:
        if current_user == user:
            return render_template('users/request.html', user=user)
        else: 
            flash("Not allow to access other than yourself!", "danger")
            return redirect(url_for('home'))
    else:
        flash("No Such User!", "danger")
        return redirect(url_for('home'))
    
@users_blueprint.route('/<fan_id>/delete_request', methods=['POST'])
@login_required
def delete_request(fan_id):
    fan = User.get_by_id(fan_id)
    
    if fan.unfollow(User.get_by_id(current_user.id)):
        flash(f"You delete {fan.username}'s request", "primary")
        return redirect(url_for('users.show_request', id=current_user.id))
    else:
        flash(f"Unable to delete this user's request, try again", "danger")
        return redirect(url_for('users.show_request', id=current_user.id))

@users_blueprint.route('/<fan_id>/approve', methods=['POST'])
@login_required
def approve(fan_id):
    fan = User.get_by_id(fan_id)

    if current_user.approve_request(fan):
        flash(f"You approve {fan.username}'s request", "primary")
        return redirect(url_for('users.show_request', id=current_user.id))
    else:
        flash(f"Unable to approve this user, try again", "danger")
    return redirect(url_for('users.show_request', id=current_user.id))

@users_blueprint.route('/<idol_id>/unfollow', methods=['POST'])
@login_required
def unfollow(idol_id):
    idol = User.get_by_id(idol_id)

    if current_user.unfollow(idol):
        flash(f"You unfollow {idol.username}", "primary")
        return redirect(url_for('users.show', username=idol.username))
    else:
        flash(f"Unable to unfollow this user, try again", "danger")
        return redirect(url_for('users.show', username=idol.username))


from flask import Blueprint, request, redirect, render_template, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from models.user import User
from flaskstagram_web.util.google_oauth import oauth

sessions_blueprint = Blueprint('sessions',
                                __name__,
                                template_folder='templates')

@sessions_blueprint.route('/new', methods=['GET'])
def new():
    return render_template('sessions/new.html')

@sessions_blueprint.route('/', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = User.get_or_none(User.username == username)
    if user:
        result = check_password_hash(user.hashed_password, password)
        if result:
            login_user(user)
            flash('You were successfully logged in', 'primary')
            return redirect(url_for('home'))
        else:
            flash('Wrong password provided. Please try again!', 'danger')
            return render_template('sessions/new.html')
    else:
        flash("User not found!", "danger")
        return render_template('sessions/new.html')

@sessions_blueprint.route('/google_login')
def google_login():
    redirect_uri = url_for('sessions.authorize', _external = True)
    return oauth.google.authorize_redirect(redirect_uri)

@sessions_blueprint.route('/authorize/google')
def authorize():
    oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user: 
        login_user(user)
        flash('You were successfully logged in', 'primary')
        return redirect(url_for('users.show',username=user.username))
    else:
        flash('No email found! Please sign up', 'danger')
        return redirect(url_for('home'))

@sessions_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were successfully logged out', 'primary')
    return redirect(url_for('home'))
        

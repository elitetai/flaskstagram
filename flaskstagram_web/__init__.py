from app import app
from flask import render_template
from flask_wtf.csrf import CSRFError
from flask_assets import Environment, Bundle
from .util.assets import bundles
from flaskstagram_web.blueprints.users.views import users_blueprint
from flaskstagram_web.blueprints.sessions.views import sessions_blueprint
from flaskstagram_web.blueprints.images.views import images_blueprint
from flaskstagram_web.blueprints.payments.views import payments_blueprint
from flaskstagram_web.util.google_oauth import oauth
from models.user import User

assets = Environment(app)
oauth.init_app(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(sessions_blueprint, url_prefix="/sessions")
app.register_blueprint(images_blueprint, url_prefix="/images")
app.register_blueprint(payments_blueprint, url_prefix="/payments")

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/")
def home():
    users = User.select() 
    return render_template('home.html', users=users)
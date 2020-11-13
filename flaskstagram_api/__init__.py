from app import app, csrf
from flask_cors import CORS

cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:*"}})

## API Routes ##
from flaskstagram_api.blueprints.users.views import users_api_blueprint
from flaskstagram_api.blueprints.sessions.views import sessions_api_blueprint
from flaskstagram_api.blueprints.images.views import images_api_blueprint


app.register_blueprint(users_api_blueprint, url_prefix='/api/users')
app.register_blueprint(sessions_api_blueprint, url_prefix='/api/sessions')
app.register_blueprint(images_api_blueprint, url_prefix='/api/images')


csrf.exempt(users_api_blueprint)
csrf.exempt(sessions_api_blueprint)
csrf.exempt(images_api_blueprint)

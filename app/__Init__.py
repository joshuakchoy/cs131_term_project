from flask import Flask
from .config import Config
from .models import db
from flask_login import LoginManager
from .models import User
import os

login_manager = LoginManager()

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    app = Flask(__name__, template_folder=template_dir, instance_relative_config=False)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        # Stub: no user lookup in prototype
        return None

    # Blueprints
    from .auth.routes import bp as auth_bp
    from .main.routes import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

from flask import Flask
from.config import Config
from .models import db
from flask_login import LoginManager
from .models import User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)

    #extentions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return None #html stub, fill in later
    
    from .auth.routes import bp as auth_bp
    from .main.routes import bp as main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
    

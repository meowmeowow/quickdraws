from flask import Flask , session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
db.UPLOAD_FOLDER = './project/static/photos'
db.PHOTOS_URI = './static/photos'
'''
class UserSession():
    def __init__(self):
        self.images = None
        self.star_bool = False
        self.start = 0
        self.user_id = None

'''
def create_app():
    
    app = Flask(__name__)

    
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000

    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    from . import models

    with app.app_context():
        db.create_all()
    
    return app

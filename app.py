from extensions import db,login_manager,bcrypt
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from models import User
import os


def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///notes.db'
    load_dotenv()
    app.secret_key=os.getenv('SECRET_KEY')

    login_manager.init_app(app)
    bcrypt.init_app(app)

    @login_manager.user_loader
    def get_user(user_id):
        return User.query.get(user_id)
    
    @login_manager.unauthorized_handler
    def unauthorized_fallback():
        return "Your are unauthorized to visit this!!"
    
    db.init_app(app)

    #route imports
    from routes import register_routes
    register_routes(app)
    migrate=Migrate(app,db)
    return app

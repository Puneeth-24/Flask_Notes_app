from extensions import db
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
import os


def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///notes.db'
    load_dotenv()
    app.secret_key=os.getenv('SECRET_KEY')
    
    db.init_app(app)

    #route imports
    from routes import register_routes
    register_routes(app)
    migrate=Migrate(app,db)
    return app

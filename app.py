from extensions import db
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///notes.db'
    app.secret_key="IT'S THE SAME TYPE OF STAND AS STAR PLATINUM"
    
    db.init_app(app)

    #route imports
    from routes import register_routes
    register_routes(app)
    migrate=Migrate(app,db)
    return app

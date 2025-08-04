from extensions import db,login_manager,bcrypt
from flask import Flask,redirect,url_for,flash
from flask_migrate import Migrate
from dotenv import load_dotenv
from blueprints.notes.models import User
import os


def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///notes.db'
    load_dotenv()
    app.secret_key=os.getenv('SECRET_KEY','default-unsafe-key')

    login_manager.init_app(app)
    bcrypt.init_app(app)

    @login_manager.user_loader
    def get_user(user_id):
        return User.query.get(user_id)
    
    db.init_app(app)

    #filters
    @app.template_filter('capitalize_title')
    def capitalize_title(titles):
        new_title=' '.join([title.capitalize() for title in  titles.split(" ")])
        return new_title
    
    #blueprint imports
    from blueprints.core.routes import core
    from blueprints.notes.routes import notes

    app.register_blueprint(core,url_prefix='/')
    app.register_blueprint(notes,url_prefix='/notes')

    @login_manager.unauthorized_handler
    def unauthorized_fallback():
        flash('Please Login to access this page')
        return redirect(url_for('core.login'))
    
    
    

    
    
    
    migrate=Migrate(app,db)
    return app

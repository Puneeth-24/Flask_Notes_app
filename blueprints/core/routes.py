from flask import render_template,request,session,flash,redirect,url_for,send_from_directory,Blueprint
from flask_login import login_user,logout_user,current_user,login_required
from blueprints.notes.models import User
from extensions import db,bcrypt
import json
from sqlalchemy.exc import SQLAlchemyError
import os,uuid

core=Blueprint('core',__name__,template_folder='templates')

@core.route('/')
def welcome():
        return render_template('core/welcome.html')
    
@core.route('/signup',methods=['GET','POST'])
def signup():
        if request.method=='GET':
            return render_template('core/signup.html')
        
        if request.method=='POST':
            username=request.form.get('username')
            password=request.form.get('password')
            
            #checking if the user exists already
            checking_user=User.query.filter_by(username=username).first()
            if  checking_user:
                flash("User already exists")
                return redirect(url_for('core.login'))
            
            hash_password=bcrypt.generate_password_hash(password)
            user=User(username=username,password=hash_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Sign up successfull')
            except Exception :
                db.session.rollback()
                flash("Something went wrong during sigining up, please try agian later!!")
            return redirect(url_for('core.welcome'))

@core.route('/login',methods=['GET','POST'])
def login():
        if request.method=='GET':
            return render_template('core/login.html')
        if request.method=='POST':
            username=request.form.get('username')
            password=request.form.get('password')

            user=User.query.filter_by(username=username).first()
            if not user:
                flash('User does not exist,please sign up')
                return redirect(url_for('core.signup'))
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('notes.home'))
            else:
                flash('Wrong password, please try again!!')
                return redirect(url_for('core.login'))
            
@core.route('/logout')
@login_required
def logout():
        logout_user()
        flash('Successfully logged out!!')
        return redirect(url_for('core.welcome'))
  
            

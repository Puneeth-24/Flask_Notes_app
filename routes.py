from flask import render_template,request,session,flash,redirect,url_for,send_from_directory
from flask_login import login_user,logout_user,current_user,login_required
from models import User,Note
from extensions import db,bcrypt
import json
from sqlalchemy.exc import SQLAlchemyError
import os,uuid

def register_routes(app):

    
    @app.route('/')
    def welcome():
        return render_template('welcome.html')
    
    @app.route('/signup',methods=['GET','POST'])
    def signup():
        if request.method=='GET':
            return render_template('signup.html')
        
        if request.method=='POST':
            username=request.form.get('username')
            password=request.form.get('password')
            
            #checking if the user exists already
            checking_user=User.query.filter_by(username=username).first()
            if  checking_user:
                flash("User already exists")
                redirect(url_for('signup'))
            
            hash_password=bcrypt.generate_password_hash(password)
            user=User(username=username,password=hash_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Sign up successfull')
            except Exception :
                db.session.rollback()
                flash("Something went wrong during sigining up, please try agian later!!")
            return redirect(url_for('welcome'))

    @app.route('/login',methods=['GET','POST'])
    def login():
        if request.method=='GET':
            return render_template('login.html')
        if request.method=='POST':
            username=request.form.get('username')
            password=request.form.get('password')

            user=User.query.filter_by(username=username).first()
            if not user:
                flash('User does not exist,please sign up')
                return redirect(url_for('signup'))
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong password, please try again!!')
                return redirect(url_for('login'))
            
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Successfully logged out!!')
        return redirect(url_for('welcome'))
            

        

    #display the notes
    @app.route('/home')
    @login_required
    def home():
        username=current_user.username
        notes=[
            (note.title,note.note,note.note_id) for note in current_user.notes
        ]
        return render_template('home.html',notes=notes,name=username)

    @app.route('/add',methods=['GET','POST'])
    @login_required
    def add_note():
        notes=[]
        if request.method=='POST':
            if "file" in request.files:
                uploaded_file=request.files.get('file')
                if uploaded_file and uploaded_file.content_type=='application/json':
                    try:
                        uploaded_json_file=json.load(uploaded_file)
                        for task in uploaded_json_file:
                            title=task['title'].strip()
                            note_content=task['note'].strip()
                            notes.append(Note(user_id=current_user.user_id,title=title,note=note_content))
                            # new_note=Note(user_id=session.get('user_id'),title=title,note=note_content)
                            # db.session.add(new_note)
                            # db.session.commit()
                    
                    except json.JSONDecodeError:
                        flash('Invalid json format','error')
    
            title=request.form.get('title','').strip()
            note_content=request.form.get('note','').strip()
            if title!='' and note_content !='':
                notes.append(Note(user_id=current_user.user_id,title=title,note=note_content))

            try:
                db.session.add_all(notes)
                db.session.commit()
                flash(f'Successfully added {len(notes)} notes', 'success')
            except SQLAlchemyError as e:
                db.session.rollback()  # Always rollback on error to keep session clean
                flash('An error occurred while adding notes.', 'error')
                print(f"Database error: {e}")
            return redirect(url_for('home'))

        return render_template('add_note.html')
    
    @app.route('/download')
    @login_required
    def download():
        user_id=session.get('user_id')
        user=User.query.get(user_id)
        tasks_as_dict=[{'title':note.title,'note':note.note}for note in user.notes]
        
        if not os.path.exists('downloads'):
            os.mkdir("downloads") 
        file_name=f"{uuid.uuid4()}.json"
        file_path=os.path.join("downloads",file_name)
        with open(file_path,'w',encoding='utf-8') as j:
            json.dump(tasks_as_dict,j,indent=2)
            
        return render_template('download_page.html',filename=file_name)

    @app.route('/download/<filename>')
    def downloadFile(filename):
        return send_from_directory('downloads',filename,as_attachment=True,download_name='task.json')    

    @app.route('/remove/<int:note_id>',methods=['DELETE'])
    @login_required
    def remove(note_id):
        try:
            note=Note.query.get(note_id)
            if note and note.user_id==current_user.user_id:
                db.session.delete(note)
                db.session.commit()
                flash('Successfully removed note')
            else:
                flash('Note not found or unauthorzied')
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong during removing')
        return "note removed"
    
    @app.template_filter('capitalize_title')
    def capitalize_title(titles):
        new_title=' '.join([title.capitalize() for title in  titles.split(" ")])
        return new_title
    
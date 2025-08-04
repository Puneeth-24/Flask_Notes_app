from flask import render_template,request,session,flash,redirect,url_for,send_from_directory,Blueprint
from flask_login import current_user,login_required
from blueprints.notes.models import Note
from extensions import db,bcrypt
import json
from sqlalchemy.exc import SQLAlchemyError
import os,uuid
from pathlib import Path

notes=Blueprint('notes',__name__,template_folder='templates')

@notes.route('/')
@login_required
def home():
    username=current_user.username
    notes=[
        (note.title,note.note,note.note_id) for note in current_user.notes
    ]
    return render_template('notes/home.html',notes=notes,name=username)

@notes.route('/add',methods=['GET','POST'])
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
            return redirect(url_for('notes.home'))

        return render_template('notes/add_note.html')

@notes.route('/download')
@login_required
def download():
        tasks_as_dict=[{'title':note.title,'note':note.note}for note in current_user.notes]
        
        curr_dir=Path(__file__).resolve().parent
        root_dir=curr_dir.parent.parent
        downloads_dir_path=root_dir/'downloads'
        if not downloads_dir_path.exists():
            downloads_dir_path.mkdir()
        file_name=f"{uuid.uuid4()}.json"
        file_path=(downloads_dir_path/file_name).absolute()
        with open(file_path,'w',encoding='utf-8') as j:
            json.dump(tasks_as_dict,j,indent=2)
            
        return render_template('notes/download_page.html',filename=file_name)

@notes.route('/download/<filename>')
@login_required
def downloadFile(filename):
    curr_dir=Path(__file__).resolve().parent
    root_dir=curr_dir.parent.parent
    downloads_dir_path=(root_dir/'downloads').absolute()
    return send_from_directory(str(downloads_dir_path),filename,as_attachment=True,download_name='task.json')    



@notes.route('/remove/<int:note_id>',methods=['DELETE'])
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
    

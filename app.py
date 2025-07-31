from flask import Flask,render_template,request,redirect,url_for,send_from_directory,jsonify,session
from flask import session,make_response
import json
import os,uuid

app=Flask(__name__)
app.secret_key="it's the same type of stand as star platinum"



#welcome page
@app.route('/',methods=['GET','POST'])
def welcome():
    if request.method=='POST':
        name=request.form.get('name')
        response=make_response(redirect(url_for('home')))
        response.set_cookie('name',name)
        return response
    return render_template('welcome.html')


#home to render tasks
@app.route('/home')
def home():
    name=request.cookies.get('name')
    if 'notes' not in session:
        session['notes']=[]
    notes=session['notes'] #list of tuples (title,notes)
    return render_template('home.html',notes=notes,name=name)

#adding tasks
@app.route('/add',methods=['GET','POST'])
def add_note():
    if request.method=='POST':
        if "file" in request.files:
            uploaded_file=request.files.get('file')
            if uploaded_file.content_type=='application/json':
                uploaded_json_file=json.load(uploaded_file)
                for task in uploaded_json_file:
                    title=task['title']
                    note=task['note']
                    session['notes'].append((title,note))
                    session.modified=True
        title=request.form.get('title')
        note=request.form.get('note')
        if title!='' and note !='':
            session['notes'].append((title,note))
            session.modified=True
        return redirect(url_for('home'))

    return render_template('add_note.html')    
    


@app.route('/download')
def download():
    notes=session['notes']
    tasks_as_dict=[{'title':title,'note':note}for title,note in notes]
    

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

@app.template_filter('capitalize_title')
def capitallize_title(titles):
    new_title=' '.join([title.capitalize() for title in  titles.split(" ")])
    return new_title

@app.route('/clear_session')
def clear_session():
    response=make_response(redirect('/'))
    response.delete_cookie('name')
    session.clear()
    return response

if __name__=='__main__':
    app.run(debug=True)
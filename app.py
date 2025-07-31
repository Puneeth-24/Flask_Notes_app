from flask import Flask,render_template,request,redirect,url_for,Response,send_from_directory,jsonify
from flask import session
import json
import os,uuid

app=Flask(__name__)
app.secret_key="it's the same type of stand as star platinum"
notes=[] #list of tuples (note,title)
#home to render tasks
@app.route('/')
def home():
    return render_template('index.html',message='Hello world')


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
                    notes.append((title,note))
        title=request.form.get('title')
        note=request.form.get('note')
        if title!='' and note !='':
            notes.append((title,note))
        return redirect(url_for('home'))

    return render_template('add_note.html')    
    

@app.route('/download')
def download():
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

@app.route('/post_tasks')
def post_tasks():
    tasks_as_dict=[{'title':title,'note':note}for title,note in notes]
    json_tasks_as_dict=jsonify(tasks_as_dict)

    return json_tasks_as_dict

@app.route('/set_data')
def set_data():
    session['name']='Puneeth'
    session['age']=20
    return render_template('index.html',message='This is set data')

@app.route('/get_data')
def get_data():
    if 'name' in session.keys() and 'age' in session.keys():
        name=session['name']
        age=session['age']
        return render_template('index.html',message=f'{name},{age}')
    return render_template('index.html',message='No data to get')

@app.route('/remove_data')
def remove_data():
    session.clear()
    return render_template('index.html',message='session was removed')

if __name__=='__main__':
    app.run(debug=True)
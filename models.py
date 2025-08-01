from extensions import db

class User(db.Model):

    __tablename__='user'

    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(150),nullable=False,unique=True)

    notes=db.relationship('Note',backref='user',lazy=True)

    def __repr__(self):
        return f"<{self.user_id}:{self.username}>"
    
class Note(db.Model):

    __tablename__='note'

    note_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    title=db.Column(db.String(100),nullable=False)
    note=db.Column(db.Text,nullable=False)

    def __repr__(self):
        return f"<{self.note_id}:{self.title}>"

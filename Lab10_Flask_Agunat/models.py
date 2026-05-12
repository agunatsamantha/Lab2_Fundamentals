from flask_sqlalchemy import SQLAlchemy 
from flask_login import UserMixin 

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='viewer') 
    display_name = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200), default='default.png')

    def __repr__(self):
        return f'<User {self.email}>'
    
class Student(db.Model): 
    __tablename__ = 'students'      
    id = db.Column(db.Integer, primary_key=True)     
    full_name = db.Column(db.String(150), nullable=False)     
    email = db.Column(db.String(150), unique=True, nullable=False) 

    def __repr__(self): 
        return f'<Student {self.full_name}>' 



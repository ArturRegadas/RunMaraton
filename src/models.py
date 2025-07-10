from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from src.support.dbInfo import user, password, DBname

app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    finalized_exercises = db.relationship('Finalized', backref='user', cascade='all, delete-orphan')

class Finalized(db.Model):
    __tablename__ = 'finalized'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('users.username', ondelete="CASCADE"))
    exercise = db.Column(db.String, nullable=False)



def load_from_db():
    users = {}
    all_users = User.query.all()
    for user in all_users:
        finalized_set = set(entry.exercise for entry in user.finalized_exercises)
        users[user.username] = {
            "password": user.password,
            "finalized": finalized_set
        }
    return users



def createUserInDb(username, password):
    newUser = User(username = username, password = password)
    db.session.add(newUser)
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
    
def addExerciceInDb(username, exercise):
    newExercice = Finalized(username = username, exercise = exercise)
    db.session.add(newExercice)
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
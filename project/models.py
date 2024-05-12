from . import db
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    images = db.relationship('Image',backref = 'owner')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    hash = db.Column(db.String,unique=True)
    length = db.Column(db.Integer)
    created = db.Column(db.DateTime,default = datetime.now)
    credit = db.Column(db.String)
    contentType = db.Column(db.String)



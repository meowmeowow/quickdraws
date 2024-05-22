
import os
from . import db
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import magic
import hashlib

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    images = db.relationship('Image', backref='owner', lazy=True)

    playlists = db.relationship('Playlist', backref='owner', lazy=True)
    
    def __repr__(self):
        return '<User %r>' % self.name

    def check_password(self, password):
        return check_password_hash(self.password, password)

def newUser(name, email, password):
  new_user = User(email=email,
                  name=name,
                  password=generate_password_hash(password, method='scrypt'))
  return new_user

class Playlist(db.Model):
     id = db.Column(db.Integer, primary_key=True)

     name = db.Column(db.String(1000))
     user_id =  db.Column(db.Integer,db.ForeignKey('user.id'))
     created = db.Column(db.DateTime,default = datetime.now)
     playlistitems = db.relationship('PlaylistItem', backref='playlist', lazy=True)


def newPlaylist(name,user_id):
  playlist = Playlist(name = name, user_id = user_id) 
  return playlist


     
class PlaylistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    playlist_id =  db.Column(db.Integer,db.ForeignKey('playlist.id'))

    image_id =  db.Column(db.Integer,db.ForeignKey('image.id'))

    created = db.Column(db.DateTime,default = datetime.now)

def newPlaylistItem(playlist_id,image_id):
  playlistitem = PlaylistItem(playlist_id = playlist_id, image_id = image_id)
  return playlistitem
    
    
    
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False, unique=True)
    length = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now)
    credit = db.Column(db.String)
    contentType = db.Column(db.String)

    #playlist_image = db.relationship('Playlist_Image', backref='playlist_image', lazy=True)

    
    def __repr__(self):
        return '<Image %s %r %s %s>' % (self.name, self.contentType, self.filename(), self.owner)

    def filename(self):
        return os.path.join(db.UPLOAD_FOLDER, self.hash)
    def uri(self):
        return os.path.join(db.PHOTOS_URI, self.hash)

    def content(self):
        return open(self.filename(), "rb").read()
        
def newImage(body):
    contenttype = magic.from_buffer(body, mime=True)
    file_hash = hashlib.sha256(body).hexdigest()

    image = Image(
        hash=file_hash,
        length = len(body),
        contentType = contenttype 
    )
    
    return image
    
        


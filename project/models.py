import os
from . import db
from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import magic
import hashlib
    
class ImageTag(UserMixin,db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    image_id =  db.Column(db.Integer,db.ForeignKey('image.id'))
    tag = db.Column(db.String(1000))
    
def getImagesFromTag(tags):
    data = []
    
    for tag_t in tags:
        images = list(ImageTag.query.filter_by(tag = tag_t))
        if not images: return

        for image in images:
            for dat in data:
                if(image.image_id != dat.image_id):
                    data.append(image)

    if(len(tags) == 0):
        data = list(Image.query.all()) # change to imagetag-> when uploading add tags
    return(data)



def newImageTag(image_id_t, tag_t):
    new_imageTag = ImageTag(
        image_id = image_id_t,
        tag = tag_t
    )
    return(new_imageTag)


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

    def get_playlists(self):
        playlists = list(Playlist.query.filter_by(user_id = self.id))
        if playlists:
            return(playlists)
        return False
def newUser(name, email, password):
  new_user = User(email=email,
                  name=name,
                  password=generate_password_hash(password, method='scrypt'))
  return new_user

class Playlist(db.Model):
     id = db.Column(db.Integer, primary_key=True)

     name = db.Column(db.String(1000))# make name+user unique, user can only have 1 playlist of each name
     user_id =  db.Column(db.Integer,db.ForeignKey('user.id'))
     created = db.Column(db.DateTime,default = datetime.now)
     playlistitems = db.relationship('PlaylistItem', backref='playlist', lazy=True)
     
     def getImagesFromPlaylist(self):
        return(list(PlaylistItem.query.filter_by(playlist_id = self.id)))

def newPlaylist(name,user_id):
    playlist = Playlist(name = name, user_id = user_id)
    return playlist



class PlaylistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    created = db.Column(db.DateTime, default=datetime.now)

    @staticmethod
    def newPlaylistItem(playlist_id, image_id):
        return PlaylistItem(playlist_id=playlist_id, image_id=image_id)
    
    
    
    

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False, unique=True)
    length = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now)
    credit = db.Column(db.String)
    contentType = db.Column(db.String)
    playlist_image = db.relationship('PlaylistItem', backref='playlist_image', lazy=True)
    image_tag = db.relationship('ImageTag', backref='image_tag', lazy=True)

    def __repr__(self):
        return f'<Image {self.name} {self.contentType} {self.filename()} {self.owner}>'

    def filename(self):
        return os.path.join(db.UPLOAD_FOLDER, self.hash)

    def uri(self):
        return os.path.join(db.PHOTOS_URI, self.hash)
    def isInPlaylist(self, user, playlistname):
        playlist = Playlist.query.filter_by(user_id = user).filter_by(name = playlistname).first()
        if playlist:
            playlist_item = PlaylistItem.query.filter_by(image_id = self.id).filter_by(playlist_id =playlist.id).first()

            return playlist_item is not None
        else:
            return False
    def setInPlaylist(self, user, playlistname):
        playlist = Playlist.query.filter_by(user_id = user).filter_by(name = playlistname).first()
        if not playlist: return

        playlist_item = PlaylistItem.newPlaylistItem(playlist.id,self.id)
        db.session.add(playlist_item)
        db.session.commit()
    def deleteInPlaylist(self,user, playlistname):
       playlist = Playlist.query.filter_by(user_id = user).filter_by(name = playlistname).first()
       if not playlist: return
       #db.session.execute(db.delete(PlaylistItem.query.filter_by(image_id = self.id).filter_by(playlist_id =playlist.id).first()))
       db.session.execute(db.delete(PlaylistItem).where(PlaylistItem.image_id == self.id).where(PlaylistItem.playlist_id == playlist.id))
       db.session.commit()
    @staticmethod
    def new_image( body):
        contenttype = magic.from_buffer(body, mime=True)
        file_hash = hashlib.sha256(body).hexdigest()
        return Image(
            hash=file_hash,
            length=len(body),
            contentType=contenttype
        )
    
        


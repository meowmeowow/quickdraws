
# imporOAAAt the Flask library
from flask import Flask, render_template, request , send_from_directory,Blueprint, flash,redirect, url_for
#import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from . import db
from .models import Image, Playlist, PlaylistItem
from . import models
from .forms import PlaylistForm
from flask import current_app as app
from werkzeug.utils import secure_filename
import os
import random
import math
import hashlib
import magic
import zipfile
from datetime import datetime
import json
import requests

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
class Session:
    def __init__(self, user_id):
        self.user_id = user_id
        self.images = None

userSession = {}
def getSession(user_id):
    session = userSession.get(user_id)
    if session is None:
        session = Session(user_id)
        userSession[user_id] = session
    return session

@main.app_context_processor
def inject_wtf():
    return dict(wtf=Form())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    #images = current_user.images
    playlist = models.Playlist.query.filter_by(user_id = current_user.id).filter_by(name = "uploaded").first()
    images = playlist.getImagesFromPlaylist()
    form = PlaylistForm()
    if form.validate_on_submit():
        flash('Playlist added successfully!')
        return redirect(url_for('main.profile'))
    return render_template('profile.html', name=current_user.name, images=images, form=form)

@main.route('/playlist')
@login_required
def playlist():
    #images = current_user.images
    playlist = models.Playlist.query.filter_by(user_id = current_user.id).filter_by(name = "uploaded").first()
    images = playlist.getImagesFromPlaylist()

    return render_template('playlist.html', name=current_user.name, images=images)

'''
@main.route("/playlist/<playlistname>/", methods=['GET'])
@login_required
def getImagesPlaylists(playlistName):
    return render_template('index.html')

'''
@main.route('/constraints')
@login_required
def constraints():
    return render_template('constraints.html')

@main.route('/upload')
@login_required
def upload():
    return render_template('upload.html')

@main.route('/upload', methods=['POST'])
@login_required
def upload_post():
    if 'files' not in request.files:
        flash('No file part')
        return redirect(request.url)

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        flash('No selected file')
        return redirect(request.url)

    for file in files:
        if file and allowed_file(file.filename):
            try:
                file_content = file.read()
                #resize here
                if file.filename.endswith('.zip'):
                    with zipfile.ZipFile(file, 'r') as zip_ref:
                        for extracted_file in zip_ref.namelist():
                            extracted_file_content = zip_ref.read(extracted_file)
                            if extracted_file_content:
                                image = models.newImage(extracted_file_content)
                                image.user_id = current_user.id
                                image.name = file.filename
                                
                                open(image.filename(), 'wb').write(file_content)

                                
                                db.session.add(image)
                                
                                #uploaded_file(image.hash)
                else:
                    image = models.newImage(file_content)
                    image.user_id = current_user.id
                    image.name = file.filename
                    
                    
                    open(image.filename(), 'wb').write(file_content)

                    db.session.add(image)
                    
                    #uploaded_file(image.hash)
            except Exception as e:
                db.session.rollback()
                flash(f"Error uploading file {file.filename}: {str(e)}")
                return redirect(request.url)

    try:
        db.session.commit()
        flash('Files uploaded successfully!')
    except Exception as e:
        db.session.rollback()
        flash(f"Database error: {str(e)}")

    return redirect(request.url)



@main.route("/playlist/<playlistname>/<num>", methods=['GET'])
def is_member_of_playlist(playlistname,num):
    num = int(num)

    print(num)

    session = getSession(current_user.id)
    num = getImageNum(session.images,num)
    img = session.images[num]
    result = img.isInPlaylist(current_user.id,playlistname)
    return(str(result))

@main.route("/playlist/<playlistname>/<num>", methods=['PUT'])
def add_to_playlist(playlistname,num):
    num = int(num)
    session = getSession(current_user.id)
    num = getImageNum(session.images,num)

    img = session.images[num]
    img.setInPlaylist(current_user.id,playlistname)
    return ("True")

@main.route("/playlist/<playlistname>/<num>", methods=['DELETE'])
def delete_from_playlist(playlistname,num):
    num = int(num)
    session = getSession(current_user.id)
    num = getImageNum(session.images,num)

    img = session.images[num]
    img.deleteInPlaylist(current_user.id,playlistname)

    return ("False")


@main.route("/image/get/<num>")
def get_img(num):   

    file_name = ""

    start = int(num)

    session = getSession(current_user.id)
    if (not session.images) or (start == 0): 
        session = getSession(current_user.id)
        session.images = list(db.session.execute(db.select(Image).order_by(Image.created)).scalars())
        random.shuffle(session.images) 

        
    images = session.images
    
    start = getImageNum(images,start)
    
    img = images[start]
    imginfo = {}
    imginfo['hash'] = str(img.hash)
    imginfo['star'] = img.isInPlaylist(current_user.id, "starred")
    imginfo = json.dumps(imginfo)

    return imginfo

def getImageNum(images,start):
    if(start == 0):
        return(0)
    if start < 0:
        rem = int((abs(start) + 1) % len(images))
        if rem == 0:
            rem = len(images)
        start = len(images) - rem

    if start > len(images) - 1:
        rem = int((abs(start) + 1) % len(images))
        if rem == 0:
            rem = len(images)
        start = rem - 1
    return(start)

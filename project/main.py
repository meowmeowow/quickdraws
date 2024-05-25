from flask import Flask, render_template, request , send_from_directory,Blueprint, flash,redirect, url_for

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
# Create the Flask instance and pass the Flask 
# constructor the path of the correct module

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    #form = PlaylistForm()
    #if form.validate_on_submit():
    #    flash('Playlist added successfully!')
    #    return redirect(url_for('main.profile'))
    #return render_template('profile.html', name=current_user.name, images=images, form=form)
    return render_template('index.html')

@main.route('/playlist/<playlistName>')
@login_required
def playlist(playlistName):
    #fix
    #images = current_user.images

    #return render_template('playlist.html', name=current_user.name, images=images)
    return render_template('index.html')

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
                if file.filename.endswith('.zip'):
                    with zipfile.ZipFile(file, 'r') as zip_ref:
                        for extracted_file in zip_ref.namelist():
                            extracted_file_content = zip_ref.read(extracted_file)
                            if extracted_file_content:
                                image = models.newImage(extracted_file_content)
                                image.user_id = current_user.id
                                image.name = extracted_file
                                db.session.add(image)
                else:
                    image = models.newImage(file_content)
                    image.user_id = current_user.id
                    image.name = file.filename
                    db.session.add(image)
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
'''  
  file = request.files['file']
  
  if file.filename == '':
    flash('No selected file')
    return redirect(request.url)
  
  if file and allowed_file(file.filename):
    body = file.read()

    image = models.newImage(body)
    image.user_id = current_user.id
    image.name = file.filename
    
    db.session.add(image)
    db.session.commit()
    open(image.filename(), 'wb').write(body)

    image.models.setInPlaylist(current_user.id,"uploaded")

    
    flash('Uploaded!')
    return redirect(request.url)
  
  flash('Please try again, there was a problem')
  return redirect(request.url)
'''
@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(main.config['UPLOAD_FOLDER'], filename)


@main.route("/playlist/<playlistname>/<num>", methods=['GET'])
def is_member_of_playlist(playlistname,num):
    #get image by the hash and call starred function with user id?
    
    session = getSession(current_user.id)
    img = session.images[num]
    result = img.isInPlaylist(current_user.id,playlistname)
    return(result)

@main.route("/playlist/<playlistname>/<num>", methods=['PUT'])
def add_to_playlist(playlistname,num):
    #handle request -> create new entry in playlistitem table

    session = getSession(current_user.id)
    img = session.images[num]
    img.setInPlaylist(current_user.id,playlistname)
    return redirect('/playlist/<playlistname>')

@main.route("/playlist/<playlistname>/<num>", methods=['DELETE'])
def delete_from_playlist(playlistname,num):
    #handle request -> delete playlistitem table
    #javascript -> make calls
    
    session = getSession(current_user.id)
    img = session.images[num]
    img.deleteInPlaylist(current_user.id,playlistname)
    return redirect('/playlist/<playlistname>')

@main.route("/getimages")
def get_images():
  #initalize images list, edit when faced with constrants
  session = getSession(current_user.id)
  session.images = list(db.session.execute(db.select(Image).order_by(Image.created)).scalars())
  random.shuffle(session.images)

  return ""

@main.route("/image/get/<num>")
def get_img(num):
    file_name = ""

    session = getSession(current_user.id)
    if not session.images: get_images()
        
    images = session.images
    print(len(images))
    start = int(num)
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
    img = images[start]
    imginfo = {}
    imginfo['hash'] = str(img.hash)
    imginfo['star'] = img.isInPlaylist(current_user.id, "starred")
    imginfo = json.dumps(imginfo)

    return imginfo


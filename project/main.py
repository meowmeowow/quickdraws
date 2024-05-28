
# imporOAAAt the Flask library
from flask import Flask, render_template, request , send_from_directory,Blueprint, flash,redirect, url_for
#import session
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from . import db
from .models import Image, Playlist, PlaylistItem
from . import models
from .forms import PlaylistForm, UploadImageForm, populate_playlist_choices
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

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    playlist = models.Playlist.query.filter_by(user_id=current_user.id).filter_by(name="uploaded").first()
    images = playlist.getImagesFromPlaylist() if playlist else []
    form = PlaylistForm()
    if form.validate_on_submit():
        new_playlist = models.Playlist(
            name=form.name.data,
            user_id=current_user.id,
        )
        db.session.add(new_playlist)
        db.session.commit()
        flash('Playlist added successfully!')
        return redirect(url_for('main.profile'))
    playlists = models.Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', name=current_user.name, images=images, playlists=playlists, form=form)

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

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_post():
    form = UploadImageForm()
    form.playlist.choices = populate_playlist_choices(current_user.id)  # Populate playlist choices
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()  # Fetch user playlists

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.new_playlist.data:
                new_playlist = Playlist(name=form.new_playlist.data, user_id=current_user.id)
                db.session.add(new_playlist)
                db.session.commit()
                playlist_id = new_playlist.id
            else:
                playlist_id = form.playlist.data

            # Get the selected playlist ID from the form
            selected_playlist_id = request.form.get('playlistselect')
            if not selected_playlist_id:
                flash('No playlist selected')
                return redirect(request.url)
            playlist_id = int(selected_playlist_id)

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
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(main.root_path, 'static/photos', filename)
                        file.save(filepath)

                        # Create and save the image entry
                        image = Image(file_path=filename, user_id=current_user.id, name=filename)
                        db.session.add(image)
                        db.session.commit()

                        # Add image to playlist
                        playlist_item = PlaylistItem(playlist_id=playlist_id, image_id=image.id)
                        db.session.add(playlist_item)
                        db.session.commit()

                    except Exception as e:
                        db.session.rollback()
                        flash(f"Error uploading file {file.filename}: {str(e)}")
                        return redirect(request.url)

            flash('Files uploaded successfully!')
            return redirect(url_for('main.profile'))

    # Ensure the form and playlists are passed to the template in GET and POST requests
    return render_template('upload.html', form=form, playlists=playlists)

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

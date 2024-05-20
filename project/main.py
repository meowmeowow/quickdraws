# import the Flask library
from flask import Flask, render_template, request , send_from_directory,Blueprint, flash,redirect, url_for
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from . import db
from .models import Image
from .models import Playlist
from .models import PlaylistItem
from . import models
from .forms import PlaylistForm


from werkzeug.utils import secure_filename

import os
import random
import math
import hashlib
import magic


# Create the Flask instance and pass the Flask 
# constructor the path of the correct module

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


images = list()
start = 0
star_bool = False


@main.app_context_processor
def inject_wtf():
    return dict(wtf=Form())


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
  return render_template('index.html',starShowing = star_bool)

@main.route('/',methods=['POST'])
def index_post():
  if request.form.get('star') == 'notstared':
    db.session.execute(db.delete(PlaylistItem).where(PlaylistItem.image_id == images[start].id).where((db.select(Playlist).where(Playlist.c.id == PlaylistItem.playlist_id)).user_id == current_user.id))
  elif request.form.get('star') == 'stared':
    playlist_item = models.newPlaylistItem((db.session.execute(db.select(Playlist).where(Playlist.c.name == "starred").where(Playlist.user_id == current_user.id))),images[start].id) 

  else:
    pass # unknown

  return ('', 204)

@main.route('/profile')
@login_required
def profile():
  images = current_user.images
  form = PlaylistForm()
  if form.validate_on_submit():
        # Handle form submission here
        # For example, save the form data to the database
        flash('Playlist added successfully!')
        return redirect(url_for('main.profile'))
  return render_template('profile.html', name=current_user.name, images=images, form=form)

@main.route('/playlist')
@login_required
def playlist():
  images = current_user.images

  return render_template('playlist.html', name=current_user.name, images=images)


@main.route('/constraints')
@login_required
def constraints():
  return render_template('constraints.html')

@main.route('/upload')
@login_required
def upload():
  return render_template('upload.html')

@main.route('/upload', methods=['POST'])
def upload_post():
  if 'file' not in request.files:
    flash('No file part')
    return redirect(request.url)
  
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



    playlist_item = models.newPlaylistItem((db.session.execute(db.select(Playlist).where(Playlist.name == "uploaded").where(Playlist.user_id == current_user.id))),image.id)
                       
    flash('Uploaded!')
    return redirect(request.url)
  
  flash('Please try again, there was a problem')
  return redirect(request.url)

@main.route('/uploads/<filename>')
def uploaded_file(filename):
  return send_from_directory(main.config[db.session.execute(db.select(PlaylistItem).where((PlaylistItem.playlist_id.name) == "uploaded").where((PlaylistItem.playlist_id.user_id) == current_user.id).order_by(Image.created)).scalars()],filename) 

@main.route("/getimages")
def get_images():
  
  global star_bool
  global images
  images = list(db.session.execute(db.select(Image).order_by(Image.created)).scalars())
  random.shuffle(images);



  #star_bool = bool(db.session.execute(PlaylistItem.query.filter_by(PlaylistItem.image_id = images[start].id).filter_by(PlaylistItem.playlist_id.id == Playlist.name == "starred").filter_by(Playlist.user_id == current_user.id)).first())

  #filter if image is in table
  #filter if in a playlist that the user has starred

  possible = list(db.session.execute(db.select(Playlist).where((Playlist.user_id) == current_user.id).where((Playlist.name) == "starred")).scalars())
  if(possible != 0):
    star_bool = bool(db.session.execute(PlaylistItem.query.filter_by(image_id = images[start].id, playlist_id = possible[0].id)).first())

  
  return str(images[0].hash)
  
@main.route("/getimage/<num>")
def get_img(num):
    file_name = ""

    global images
    global start
    global star_bool
    
    
    start = int(num)

    
    if start < 0:
      rem = int((abs(start)+1) % len(images))
      if rem == 0:
        rem = len(images)

      start = len(images)-rem
    
    if start > len(images)-1:
      rem = int((abs(start)+1) % len(images))
      if rem == 0:
        rem = len(images)
      
      start = rem-1      

    possible = list(db.session.execute(db.select(Playlist).where((Playlist.user_id) == current_user.id).where((Playlist.name) == "starred")).scalars())
    if(possible != 0):
      star_bool = bool(db.session.execute(PlaylistItem.query.filter_by(image_id = images[start].id, playlist_id = possible[0].id)).first())



    return str(images[start].hash)


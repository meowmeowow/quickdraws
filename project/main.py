# import the Flask library
from flask import Flask, render_template, request , send_from_directory,Blueprint, flash,redirect
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from . import db
from .models import Image

from werkzeug.utils import secure_filename

import os
import random
import math
import hashlib
import magic


# Create the Flask instance and pass the Flask 
# constructor the path of the correct module

main = Blueprint('main', __name__)

UPLOAD_FOLDER  = './project/static/photos'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
#main.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER





if 0:
  file_names = list()
  for root, dirc, files in os.walk(UPLOAD_FOLDER, topdown=True):

    for FileName in files:
      file_names.append(FileName)
      
start = 0



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def index():
  return render_template('index.html')

@main.route('/',methods=['POST'])
def index_post():

  if request.form.get('star') == 'notstared':
    pass
  elif request.form.get('star') == 'stared':
    pass
  else:
    pass # unknown

  return ('', 204)





@main.route('/profile')
@login_required
def profile():
  return render_template('profile.html', name=current_user.name)




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
    contenttype = magic.from_buffer(body)


    file_hash = hashlib.sha256(body).hexdigest()
    filename = os.path.join(UPLOAD_FOLDER,file_hash)

    open(filename,'wb').write(body)

    image = Image(
            owner_id=current_user.id,
            hash=file_hash,
            length = len(body),
            contentType = contenttype 
        )


    db.session.add(image)
    db.session.commit()

    flash('Uploaded!')
    return redirect(request.url)




  
  flash('Please try again, there was a problem')
  return redirect(request.url)










@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(main.config[db.session.execute(db.select(Image).order_by(Image.location)).scalars()],
                               filename)



@main.route("/getimage")
def get_img():
    file_name = ""
    file_names = list()
    if (request.args.get("num") != None and (len(file_names) != 0)):

        start = int(request.args.get("num"))

        if(start < 0):
          rem = int((abs(start)+1)%len(file_names))
          if (rem == 0):
            rem = len(file_names)

          start = len(file_names)-rem

        if(start >(len(file_names)-1)):
          rem = int((abs(start)+1)%len(file_names))
          if (rem == 0):
            rem = len(file_names)
          start = rem-1;


        
        return str(file_names[start])


    else:
  
      image_list = Image.query.all()

      for img in image_list:
        file_names.append(img.hash)
      

      
      ## add database entrys from image table to file_names list
      
      random.shuffle(file_names);

      return str(file_names[0])


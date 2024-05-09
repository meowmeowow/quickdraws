# import the Flask library
from flask import Flask, render_template, request , send_from_directory,Blueprint
from flask_login import login_required, current_user

import os
import random
import math
# Create the Flask instance and pass the Flask 
# constructor the path of the correct module

main = Blueprint('main', __name__)


file_names = list()
path1 = 'static/photos'
for root, dirc, files in os.walk(path1):
  for FileName in files:
    file_names.mainend(FileName)
start = 0;

@main.route('/')
def index():
  return render_template('index.html')
@main.route('/profile')
@login_required
def profile():
  return render_template('profile.html', name=current_user.name)

@main.route("/figuredrawing")
def figuredrawing():
    return send_from_directory('templates', 'main.html')



@main.route("/getimage")
def get_img():
    if (request.args.get("num") != None):

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
      random.shuffle(file_names);

      return str(file_names[0])


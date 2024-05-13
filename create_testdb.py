#!/usr/bin/env python3

import os
import hashlib

import project
import magic
from werkzeug.security import generate_password_hash, check_password_hash

from project import models

if 1:
    os.unlink('./instance/db.sqlite')

app = project.create_app()

with app.app_context():
    db = project.db

    if 1:
        users = []
        users.append(("hana", "hanahassan@willowmail.com", "1234"))
        users.append(("Scott", "hassan@willowmail.com", "1234"))

        for user in users:
            new_user = models.User(email=user[1],
                            name=user[0],
                            password=generate_password_hash(user[2],
                                                            method='scrypt'))
            db.session.add(new_user)

        users = db.session.execute(db.select(models.User)).scalars()

        current_user = users.first()
        
        files = os.listdir(db.UPLOAD_FOLDER)
        for fn in files:
            print(fn)
            filename = os.path.join(db.UPLOAD_FOLDER, fn)

            body = open(filename, "rb").read()
            image = models.newImage(body)
            
            image.user_id = current_user.id
            
            db.session.add(image)

        db.session.commit()
    
    

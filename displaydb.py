#!/usr/bin/env python3

import project
from project import models

app = project.create_app()

with app.app_context():
    db = project.db

    if 1:
        stmt = db.select(models.User)
        for row in db.session.execute(stmt).scalars():
            print(row)
            print(row.images)

    if 1:
        stmt = db.select(models.Image).order_by(models.Image.created)
        for row in db.session.execute(stmt).scalars():
            print(row)


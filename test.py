#!/usr/bin/env python3

import os
import project
import magic
from project.models import Image

app = project.create_app()
with app.app_context():
    db = project.db

    if 1:
        stmt = db.select(Image).order_by(Image.created)
        for row in db.session.execute(stmt).scalars():
            print(row)
            print(row.hash, row.created, row.length, row.contentType)
            print(row.owner)





from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, validators
from flask_wtf.file import FileField, FileAllowed, FileRequired

class PlaylistForm(Form):
    name = StringField("Playlist Name")
    category = StringField("Category")
    logo = FileField("Upload a cover for your playlist", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Can only upload photos!')])
    submit = SubmitField('Submit')
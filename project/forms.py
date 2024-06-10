# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from .models import Playlist

class PlaylistForm(FlaskForm):
    name = StringField("Playlist Name")
    category = StringField("Category")
    logo = FileField("Upload a cover for your playlist", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Can only upload photos!')])
    submit = SubmitField('Submit')

class UploadImageForm(FlaskForm):
    image = FileField('Image', validators=[DataRequired()])
    playlist = SelectField('Playlist', choices=[], coerce=int)
    submit = SubmitField('Upload')

def populate_playlist_choices(user_id):
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return [(playlist.id, playlist.name) for playlist in playlists]
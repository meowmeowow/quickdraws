from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, validators, SelectField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from .models import Playlist


class PlaylistForm(Form):
    name = StringField("Playlist Name")
    category = StringField("Category")
    logo = FileField("Upload a cover for your playlist", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Can only upload photos!')])
    submit = SubmitField('Submit')

def populate_playlist_choices(user_id):
    playlists = Playlist.query.filter_by(user_id=user_id).all()
    return [(playlist.id, playlist.name) for playlist in playlists]

class UploadImageForm(Form):
    image = FileField('Image', validators=[DataRequired()])
    playlist = SelectField('Playlist', choices=[], coerce=int)
    new_playlist = StringField('New Playlist')
    submit = SubmitField('Upload')
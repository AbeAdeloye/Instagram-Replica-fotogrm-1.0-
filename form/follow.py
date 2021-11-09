from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms import Form, validators


class comment(Form):
    id = HiddenField('pid')
    txt = StringField('name')

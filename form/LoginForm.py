from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms import Form, validators


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')
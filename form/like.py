from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms import Form, validators


class like(Form):
    id = HiddenField('pid')
    submitField = SubmitField('like')

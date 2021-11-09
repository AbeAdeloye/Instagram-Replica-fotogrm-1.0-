import datetime

from firebase_admin import db
from flask_bcrypt import generate_password_hash
from google.cloud import ndb


class user(ndb.Model):
    username = ndb.StringProperty(unique=True)
    email = ndb.StringProperty(unique=True)
    timestamp = ndb.DateTimeProperty(default=datetime.datetime.now)


class followers(ndb.Model):
    f = ndb.KeyProperty(repeated=True)


class following(ndb.Model):
    f = ndb.KeyProperty(repeated=True)


class post(ndb.Model):
    timestamp = ndb.StringProperty()
    author = ndb.StringProperty()
    photoid = ndb.StringProperty()
    likes = ndb.KeyProperty()
    comments = ndb.KeyProperty()


class likes(ndb.Model):
    likecount = ndb.IntegerProperty()
    likers = ndb.KeyProperty(repeated=True)


class comment(ndb.Model):
    timestamp = ndb.DateTimeProperty()
    comment = ndb.StringProperty()
    author = ndb.KeyProperty()


class comments(ndb.Model):
    ndb.StructuredProperty(comment, repeated=True)

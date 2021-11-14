import datetime

from firebase_admin import db
from flask_bcrypt import generate_password_hash
from google.cloud import ndb


class user(ndb.Model):
    """
    User model
    Contains username, email, timestamp, followers, following, posts, ppic, and bio.
    """
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(default=datetime.datetime.now)
    followers = ndb.KeyProperty()
    following = ndb.KeyProperty()
    posts = ndb.KeyProperty()
    ppic = ndb.StringProperty()
    bio = ndb.StringProperty()


class followers(ndb.Model):
    """
    Followers model.
    Contains keys for followers.
    """
    f = ndb.KeyProperty(repeated=True)


class following(ndb.Model):
    """
    Following model.
    Contains keys for following.
    """
    f = ndb.KeyProperty(repeated=True)


class uposts(ndb.Model):
    """
    User posts model.
    Contains keys for a users posts.
    """
    posts = ndb.KeyProperty(repeated=True)


class post(ndb.Model):
    """
    Post model.
    Contains timestamp, author, photoID, likes, and comments.
    """
    title=ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(default=datetime.datetime.now)
    author = ndb.StringProperty()
    pic = ndb.StringProperty()
    likes = ndb.KeyProperty()
    comments = ndb.KeyProperty()


class likes(ndb.Model):
    """
    Likes model.
    Contains likecount and likers.
    """
    likecount = ndb.IntegerProperty()
    likers = ndb.KeyProperty(repeated=True)


class comment(ndb.Model):
    """
    Comment model.
    Contains timestamp, comment, and author.
    """
    timestamp = ndb.DateTimeProperty()
    text = ndb.StringProperty()
    author = ndb.KeyProperty()


class comments(ndb.Model):
    """
    Comments model.
    Contains structured property.
    """
    cms = ndb.StructuredProperty(comment, repeated=True)

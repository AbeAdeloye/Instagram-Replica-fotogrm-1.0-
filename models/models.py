import datetime
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
    num = ndb.IntegerProperty()
    f = ndb.StringProperty(repeated=True)


class following(ndb.Model):
    """
    Following model.
    Contains keys for following.
    """
    num = ndb.IntegerProperty()
    f = ndb.StringProperty(repeated=True)


class uposts(ndb.Model):
    """
    User posts model.
    Contains keys for a users posts.
    """
    num = ndb.IntegerProperty()
    posts = ndb.KeyProperty(repeated=True)


class post(ndb.Model):
    """
    Post model.
    Contains timestamp, author, photoID, likes, and comments.
    """
    title = ndb.StringProperty()
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
    likers = ndb.StringProperty(repeated=True)


class comment(ndb.Model):
    """
    Comment model.
    Contains structured property.
    """
    author = ndb.StringProperty()
    text = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty(default=datetime.datetime.now)


class comments(ndb.Model):
    """
    Comments model.
    Contains structured property.
    """
    num = ndb.IntegerProperty()
    comments = ndb.KeyProperty(repeated=True)

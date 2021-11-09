from flask_login import UserMixin
#from datastore_entity import DatastoreEntity, EntityValue
from google.appengine.ext import ndb
import datetime
'''
class post(ndb.Model):
    timestamp = ndb.StringProperty()
    profileid = ndb.StringProperty()
    photoid = ndb.StringProperty()
    likeCount = ndb.StringProperty()
    comments = ndb.StringListProperty()


class postrcv(ndb.Model):
    postreceivers = ndb.StringListProperty()


indexes = postrcv.all(keys_only = True).filter('receivers = ', uid)
keys = [k.parent() for k in indexes]
messages = db.get(keys)


class profile(ndb.Model):
    uid = ndb.StringProperty()
    ppicid = ndb.StringProperty()
    username = ndb.StringProperty()


class usertimeline(ndb.Model):
    postids = ndb.StringListProperty()


class profileInteractsWith(ndb.Model):
    name = ndb.StringProperty()
    posts = ndb.StringListProperty()  # Stored as id's
    followers = ndb.StringListProperty()  # Stored as uids
    following = ndb.StringListProperty()  # stored as uids

class User(DatastoreEntity, UserMixin):
    username = EntityValue(None)
    password = EntityValue(None)
    status = EntityValue(1)
    date_created = EntityValue(datetime.datetime.utcnow())

    def authenticated(self, password):
        pass
'''
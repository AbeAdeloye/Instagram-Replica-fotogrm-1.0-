from google.cloud.datastore import db


class post(db.Model):
    timestamp = db.StringProperty()
    profileid = db.StringProperty()
    photoid = db.StringProperty()
    likeCount = db.StringProperty()
    comments = db.StringListProperty()


class postrcv(db.Model):
    postreceivers = db.StringListProperty()


indexes = postrcv.all(keys_only = True).filter('receivers = ', uid)
keys = [k.parent() for k in indexes]
messages = db.get(keys)


class profile(db.Model):
    uid = db.StringProperty()
    ppicid = db.StringProperty()
    username = db.StringProperty()


class userTimeline(db.Model):
    postids = db.StringListProperty()


class profileInteractsWith(db.Model):
    name = db.StringProperty()
    posts = db.StringListProperty()  # Stored as id's
    followers = db.StringListProperty()  # Stored as uids
    following = db.StringListProperty()  # stored as uids


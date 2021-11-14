import json
import logging
from flask import Flask, render_template, redirect, url_for, session
from google.cloud import datastore
from flask import request
import flask
import google.cloud.datastore.client
import requests

import firebase_admin
from firebase_admin import credentials, auth, firestore
from google.cloud import ndb
from google.cloud import storage
import datetime
from models.models import user, following, followers, post, likes, comments, uposts, comment

config = {
    "apiKey": "AIzaSyATS5J03pAt_LJliBweODydObkCpWTuBJc",
    "authDomain": "social-333902.firebaseapp.com",
    "projectId": "social-333902",
    "storageBucket": "social-333902.appspot.com",
    "messagingSenderId": "410902085253",
    "databaseURL": "/",
    "appId": "1:410902085253:web:0cf2c09d952e7eaae2b3ec",
    "measurementId": "G-QXFW1LCKY3"
};
api_key = "AIzaSyATS5J03pAt_LJliBweODydObkCpWTuBJc"

app = Flask(__name__,
            static_folder='/static',
            template_folder='templates')
app.secret_key = 'supersecret'
app.config['SESSION_TYPE'] = 'filesystem'
credential = credentials.Certificate("keys/firebase.json")
firebase = firebase_admin.initialize_app(credential)

storageClient = storage.Client.from_service_account_json('keys/fotoadmin.json')
bucket = storageClient.get_bucket("foto-334006.appspot.com")

ddb = firestore.client()

ds = google.cloud.ndb.Client.from_service_account_json('keys/fotoadmin.json')
dsa = datastore.Client.from_service_account_json('keys/fotoadmin.json')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message = "Check your credentials"
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        if email is None or password is None:
            return render_template("signup.html", message="Error missing email or password", action="/signup")
        print(email)
        print(password)
        try:
            user_record = auth.create_user(email=email, password=password)
            uid = user_record.uid
            with ds.context():  # <- you need this line
                flr = followers(f=[], id=uid)
                flr.put()
                fli = following(f=[], id=uid)
                fli.put()
                up = uposts(posts=[], id=uid)
                up.put()
                usr = user(email=email,
                           bio="",
                           username=username,
                           followers=flr.key,
                           following=fli.key,
                           posts=up.key,
                           timestamp=datetime.datetime.now(tz=None),
                           ppic="",
                           id=uid)
                usr.put()
            print('Sucessfully created new user: {0}'.format(uid))
            return render_template("signup.html", message="Successfully created user, {user.uid}", action="/signin")
        except Exception as e:
            print(e)
            return render_template("signup.html", message="Error creating template", action="/signup")
    return render_template("signup.html", action="/signup")


@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        print(email)
        print(password)
        if email is None or password is None:
            return render_template("signin.html", message="Error missing email or password", action="/signin")
        try:
            user = sign_in_with_email_and_password(email=email, password=password)
            print(user)
            token = user['idToken']
            session['user'] = token
            print(token)
            return flask.redirect("/")
        except Exception as e:
            print(e)
            return render_template("signin.html", message="There was an error logging in.")
    return render_template("signin.html")


@app.route('/', methods=['GET', 'POST'])
def home():
    decoded_token = auth.verify_id_token(session['user'])
    uid = decoded_token['uid']
    reconstructposts = {}
    with ds.context():
        posts = post.query()
        for pos in posts:
            aut = user.get_by_id(pos.author)
            coms = {}
            print(comments.get_by_id(pos.comments.get().key.id()))
            if comments.get_by_id(pos.comments.get().key.id()) is not None:
                for com in comments.get_by_id(pos.comments.id()):
                    comauth = ds
                    author = aut.username
                    authorid = aut.id
                    text = com.comment
                    tstamp = com.timestamp
            print(pos.key.id())
            lks = likes.get_by_id(pos.likes.key.id())
            print(likes.get_by_id(pos.likes.key.id()))
            reconstructposts.update({pos: {"author": aut.username,
                                           "comments": coms,
                                           "timestamp": pos.timestamp,
                                           "likes": lks.likecount,
                                           "pic": pos.pic
                                           }})
    print(reconstructposts)

    return render_template('home.html', posts=reconstructposts)


@app.route("/post", methods=['GET', 'POST'])
def p():
    if request.method == "POST":
        title = request.form['title']
        file = request.files
        print(file)
        decoded_token = auth.verify_id_token(session['user'])
        uid = decoded_token['uid']
        with ds.context():
            rid = post.allocate_ids(size=1)[0].id()
            comid = comments.allocate_ids(size=1)[0].id()
            lid = likes.allocate_ids(size=1)[0].id()
            print(rid)
            fLink = uploadFile(file.get('file'), str(rid))
            com = comments(cms=[], id=comid)
            lk = likes(likecount=0, likers=[], id=lid)
            pst = post(author=uid,
                       comments=ndb.Key(comments, comid),
                       likes=ndb.Key(likes, lid),
                       title=title,
                       pic=fLink,
                       timestamp=datetime.datetime.now(tz=None),
                       id=rid)
            upo = uposts.get_by_id(uid)
            pos = list(upo.posts)
            pos.append(ndb.Key(post, rid))
            upo.posts = pos
            com.put()
            lk.put()
            pst.put()
            upo.put()
    return render_template("post.html")


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


def uploadFile(f, id):
    blob = bucket.blob(id)
    blob.upload_from_file(f)
    return blob.public_url


def sign_in_with_email_and_password(email, password):
    request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(request_ref, headers=headers, data=data)
    raise_detailed_error(request_object)
    return request_object.json()


def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(e, request_object.text)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)

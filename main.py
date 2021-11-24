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


@app.route('/search', methods=["GET", "POST"])
def search():
    print("ah")
    if request.method == "GET":
        us = request.form.get('search')
        with ds.context():
            usr = dsa.query(kind="username")
            usr.add_filter("username", "<", us)

            return render_template("search.html", results=usr.fetch())


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
        foll = following.get_by_id(str(uid)).f
        print(foll)
        if len(foll) != 0:
            quer = post.query().filter(post.author.IN(list(foll))).order(-post.timestamp).fetch(limit=50)
            for q in quer:
                print(q)
            for pos in quer:
                reconstructposts[pos.key.id()] = postfix(pos, 5)
    if request.method == "POST":
        with ds.context():
            idval = request.form.get('custID').split(".")
            idd = str(idval[0])
            typ = idval[1]
            print(idd)
            print(typ)
            if typ == "comm":
                comm = comments.get_by_id(id=idd)
                commen = request.form.get("commen")
                comma = comment(text=commen, author=uid, timestamp=datetime.datetime.now(tz=None))
                comma.put()
                if comm is None:
                    comm = comments(id=idd, comments=[comma.key])
                    comm.put()
                else:
                    comm.comments.append(comma.key)
                    comm.put()
            else:
                lk = likes.get_by_id(id=int(idd))
                print(lk)
                if uid in lk.likers:
                    lk.likers.remove(uid)
                    lk.likecount -= 1
                else:
                    lk.likers.append(uid)
                    lk.likecount += 1
                lk.put()

    return render_template('home.html', posts=reconstructposts, uid=uid)


@app.route("/post", methods=['GET', 'POST'])
def p():
    if request.method == "POST":
        title = request.form['title']
        file = request.files
        decoded_token = auth.verify_id_token(session['user'])
        uid = decoded_token['uid']
        with ds.context():
            rid = post.allocate_ids(size=1)[0].id()
            comid = comments.allocate_ids(size=1)[0].id()
            lid = likes.allocate_ids(size=1)[0].id()
            fLink = uploadFile(file.get('file'), str(rid))
            com = comments(comments=[], id=rid)
            lk = likes(likecount=0, likers=[], id=rid)
            pst = post(author=uid,
                       comments=ndb.Key(comments, rid),
                       likes=ndb.Key(likes, rid),
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


def postfix(pos, maxComments):
    aut = user.get_by_id(pos.author)
    coms = {}
    pid = pos.key.id()
    extend = False
    if comments.get_by_id(str(pid)) is not None:
        i = 0
        com = comment.query().filter(comment.key.IN(comments.get_by_id(str(pid)).comments)).order(
            -post.timestamp).fetch(limit=maxComments + 1)
        if len(com) > maxComments:
            extend = True
            for comm in range(maxComments):
                authom = user.get_by_id(com[comm].author)
                author = authom.username
                authorid = com[comm].author
                text = com[comm].text
                tstamp = com[comm].timestamp
                coms[i] = {"author": author, "uid": authorid, "text": text, "tstamp": tstamp}
                i += 1
        else:
            for comm in range(len(com)):
                authom = user.get_by_id(com[comm].author)
                author = authom.username
                authorid = com[comm].author
                text = com[comm].text
                tstamp = com[comm].timestamp
                coms[i] = {"author": author, "uid": authorid, "text": text, "tstamp": tstamp}
                i += 1
        print(coms)
    lks = likes.get_by_id(pos.likes.id())
    return {"author": aut.username, "uid": pos.author, "comments": coms, "timestamp": pos.timestamp,
            "likes": lks.likecount, "pic": pos.pic, "extend": extend}


@app.route('/i/<pid>', methods=["GET", "POST"])
def postpage(pid):
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        idd = decoded_token['uid']
        pos = postfix(post.get_by_id(int(pid)), 25)
        return render_template("ipost.html", uid=idd, post=pos)


@app.route('/p/<uid>', methods=['GET', 'POST'])
def profilepage(uid):
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        idd = decoded_token['uid']
        us = user.get_by_id(idd)
        profile = user.get_by_id(uid)
        prfolw = followers.get_by_id(uid).num
        prfoli = following.get_by_id(uid).num
        reconstructposts = {}
        posts = quer = post.query().filter(post.author == uid).order(-post.timestamp).fetch()
        totalposts = len(posts)
        for pos in posts:
            reconstructposts[pos.key.id()] = postfix(pos, 5)
        flws = followers.get_by_id(uid)
        flin = following.get_by_id(idd)
        if request.method == 'POST':
            if idd not in flws.get_by_id(uid).f:
                print("AHA")
                flws.f.append(idd)
                flin.f.append(uid)
                flws.num += 1
                flin.num += 1
            else:
                if len(flws.get_by_id(uid).f) > 0:
                    print("HAH")
                    flws.f.remove(idd)
                    flin.f.remove(uid)
                    flws.num -= 1
                    flin.num -= 1
            flws.put()
            flin.put()
        if uid == idd:
            return render_template('profile.html', profile=profile, pid=uid, numposts=totalposts, followers=prfolw,
                                   following=prfoli, posts=reconstructposts, user=us, uid=idd)
        else:
            if idd not in flws.get_by_id(uid).f:
                foll = "Follow"
            else:
                foll = "Unfollow"
            return render_template('profile.html', profile=profile, pid=uid, numposts=totalposts, followers=prfolw,
                                   following=prfoli, posts=reconstructposts, user=us, uid=idd, foll=foll)


@app.route('/p/<uid>/followers')
def proffollowers(uid):
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        idd = decoded_token['uid']
        f = followers.get_by_id(uid).f
        print(f)
        combined = {}
        i = 0
        for p in f:
            combined[i] = {'uid': p, 'uname': user.get_by_id(p).username}
            i += 1
        return render_template('fol.html', results=combined, uid=uid)


@app.route('/p/<uid>/following')
def proffollowing(uid):
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        idd = decoded_token['uid']
        f = following.get_by_id(uid).f
        combined = {}
        i = 0
        for p in f:
            combined[i] = {'uid': p, 'uname': user.get_by_id(p).username}
            i += 1
        print(combined)
        return render_template('fol.html', results=combined, uid=uid)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


def uploadFile(f, id):
    blob = bucket.blob(id + ".png")
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

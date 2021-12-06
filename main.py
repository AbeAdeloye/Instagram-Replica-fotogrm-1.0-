import json
import logging
import requests

from flask import Flask, render_template, session, request, redirect
import flask

from google.cloud import datastore
from google.cloud import ndb
from google.cloud import storage
import google.cloud.datastore.client

import firebase_admin
from firebase_admin import credentials, auth

import datetime
from models.models import user, following, followers, post, likes, comments, uposts, comment

api_key = "AIzaSyATS5J03pAt_LJliBweODydObkCpWTuBJc"
app = Flask(__name__,
            static_folder='/static',
            template_folder='templates')
app.secret_key = 'supersecret'
app.config['SESSION_TYPE'] = 'filesystem'

firebase = firebase_admin.initialize_app(credentials.Certificate("keys/firebase.json"))

ds = google.cloud.ndb.Client.from_service_account_json('keys/fotoadmin.json')
dsa = datastore.Client.from_service_account_json('keys/fotoadmin.json')
storageClient = storage.Client.from_service_account_json('keys/fotoadmin.json')

bucket = storageClient.get_bucket("foto-334006.appspot.com")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Signin routing and methods
    :return:
    """
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
            print(uid)
            with ds.context():  # <- you need this line
                flr = followers(f=[], id=uid)
                fli = following(f=[], id=uid)
                up = uposts(posts=[], id=uid)
                flr.put()
                fli.put()
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
                print(usr)
                return redirect("/signin")
        except Exception as e:
            print(e)
            return render_template("signup.html", message="Error creating template", action="/signup")
    return render_template("signup.html", action="/signup")


@app.route('/signin', methods=["GET", "POST"])
def signin():
    """
    Signin routing and methods
    Renders signin template and signs in a user.
    """
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        print(email)
        print(password)
        if email is None or password is None:
            return render_template("signin.html", message="Error missing email or password", action="/signin")
        try:
            us = sign_in_with_email_and_password(email=email, password=password)
            session['user'] = us['idToken']
            return flask.redirect("/")
        except Exception as e:
            print(e)
            return render_template("signin.html", message="There was an error logging in.")
    return render_template("signin.html")


@app.route('/search', methods=["GET", "POST"])
def search():
    """
    Searches the database for users that start with what's queried.
    :return:
    """
    if request.method == "GET":
        us = request.values.get('q')
        print(request.values)
        with ds.context():
            usr = user.query().filter(user.username >= us).filter(user.username < str(us+"\ufffd"))
            return render_template("search.html", results=usr.fetch())


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Homepage routing and methods
    Renders template home.html
    """
    decoded_token = auth.verify_id_token(session['user'])
    uid = decoded_token['uid']
    reconstructposts = {}
    with ds.context():
        followi = following.get_by_id(str(uid))
        if followi is not None:
            foll = followi.f
            print(foll)
            if len(foll) != 0:
                quer = post.query().filter(post.author.IN(list(foll))).order(-post.timestamp).fetch(limit=50)
                for q in quer:
                    print(q)
                for pos in quer:
                    reconstructposts[pos.key.id()] = postfix(pos, 5)
    if request.method == "POST":
        with ds.context():
            idval = request.form.get('custID')
            if idval is not None:
                idval = idval.split(".")
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
    """
    Posting methods and routing
    Gets file and uploads
    """
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
    """
    :param pos:
    :param maxComments:
    :return fixed post (all queries worked out):
    """
    aut = user.get_by_id(pos.author)
    coms = {}
    pid = pos.key.id()
    extend = False
    if comments.get_by_id(str(pid)) is not None:
        i = 0
        com = comment.query().filter(comment.key.IN(comments.get_by_id(str(pid)).comments)).order(
            -post.timestamp).fetch(limit=maxComments + 1)
        rng = 0
        if len(com) > maxComments:
            extend = True
            rng = maxComments
        else:
            rng = len(com)
        for comm in range(rng):
            authom = user.get_by_id(com[comm].author)
            author = authom.username
            authorid = com[comm].author
            text = com[comm].text
            tstamp = com[comm].timestamp
            coms[i] = {"author": author, "uid": authorid, "text": text, "tstamp": tstamp}
            i += 1
        print(coms)
    lks = likes.get_by_id(pos.likes.id())
    return {"author": aut.username, "title": pos.title, "uid": pos.author, "comments": coms, "timestamp": pos.timestamp,
            "likes": lks.likecount, "pic": pos.pic, "extend": extend}


@app.route('/i/<pid>', methods=["GET", "POST"])
def postpage(pid):
    """
    Post page method
    :param pid:
    :return rendered template:
    """
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        uid = decoded_token['uid']
        if request.method == 'POST':
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
        pos = postfix(post.get_by_id(int(pid)), 25)
        return render_template("ipost.html", uid=idd, post=pos)


@app.route('/p/<uid>', methods=['GET', 'POST'])
def profilepage(uid):
    """
    Profile Page
    :param uid:
    :return rendered template of profile.html:
    """
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
            idval = request.form.get('custID').split(".")
            if idval is not None:
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
    """
    Gets the page for followers for a user
    :param uid:
    :return:
    """
    with ds.context():
        decoded_token = auth.verify_id_token(session['user'])
        idd = decoded_token['uid']
        f = followers.get_by_id(uid).f
        combined = {}
        i = 0
        for p in f:
            print(p)
            combined[i] = {'uid': p, 'uname': user.get_by_id(p).username}
            i += 1
        return render_template('fol.html', results=combined, uid=uid)


@app.route('/p/<uid>/following')
def proffollowing(uid):
    """
    Gets the page for users a user follows
    :param uid:
    :return:
    """
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
    """
    Handles 500 error
    :param e:
    :return:
    """
    logging.exception('An error occurred during a request.')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


@app.errorhandler(404)
def server_error(e):
    """
    Handles 404 error
    :param e:
    :return:
    """
    logging.exception('Page not found')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 404


def uploadFile(f, id):
    """
    Uploads file
    :param f:
    :param id:
    :return url:
    """
    blob = bucket.blob(id + ".png")
    blob.upload_from_file(f)
    return blob.public_url


def sign_in_with_email_and_password(email, password):
    """
    Gets auth token.
    :param email:
    :param password:
    :return:
    """
    req = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(api_key)
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    reques = requests.post(req, headers=headers, data=data)
    raise_error(reques)
    return reques.json()


def raise_error(request_object):
    """
    Raises error
    :param request_object:
    :return:
    """
    try:
        request_object.raise_for_status()
    except requests.HTTPError as e:
        raise requests.HTTPError(e, request_object.text)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)

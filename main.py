import json
import logging
from flask import Flask, render_template, redirect, url_for, session
from google.cloud import datastore
from flask import request
import flask
from flask_login import login_user
from models import user
from google.cloud import datastore
import google.cloud.datastore.client
import requests

import firebase_admin
from firebase_admin import credentials, storage, auth, db, firestore
import pyrebase
import datetime
from models.models import User, Relationship, post, postrcv, profile

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

app = Flask(__name__,
            static_folder='/static',
            template_folder='templates')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
credential = credentials.Certificate("keys/firebase.json")
firebase = firebase_admin.initialize_app(credential)

pb = pyrebase.initialize_app(config)
bucket = storage.bucket("social-333902.appspot.com")
ddb = firestore.client()


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
            ddb.collection("followers").document(uid).set({'f': []})
            ddb.collection("following").document(uid).set({'f': []})
            ddb.collection("uposts").document(uid).set({'f': []})
            ddb.collection("users").document(uid).set({u"bio": u"",
                                                       u"followers": ddb.collection("followers").document(uid),
                                                       u"following": ddb.collection("followings").document(uid),
                                                       u"posts": ddb.collection("uposts").document(uid),
                                                       u"ppic": ":/gs",
                                                       "timestamp": datetime.datetime.now(tz=datetime.timezone.utc),
                                                       "username": username})
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
            user = pb.auth().sign_in_with_email_and_password(email=email, password=password)
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
    posts = ddb.collection('post').stream()
    postsa = {doc.id: doc.to_dict() for doc in posts}
    print(postsa)
    reconstructposts = {}
    for post in postsa:
        dict = postsa.get(post)
        author = dict['author'].get().to_dict()['username']
        comments = {dict['author'].get().to_dict()['username']: dict['comment'] for dict in
                    list(dict['comments'].get().to_dict()['c'])}
        likes = 125

        reconstructposts.update({post: {"author": author,
                                        "comments": comments,
                                        "timestamp": dict['timestamp'],
                                        "likes": likes,
                                        "pic": dict['pic']
                                        }})
    print(reconstructposts)

    return render_template('home.html', posts=reconstructposts)


@app.route("/post", methods=['GET', 'POST'])
def post():
    if request.method == "POST":
        decoded_token = auth.verify_id_token(session['user'])
        uid = decoded_token['uid']
        ref = ddb.collection('post').document()
        rid = ref.id
        ddb.collection('post').document(rid).set({
            "author": ddb.collection("users").document(uid),
            "comments": ddb.collection("comments").document(rid),
            "likes": ddb.collection("likes").document(rid),
            "title": "Cool title",
            "pic": "gs://social-333902.appspot.com/ahmed-saeed-3oY6iqvc2sg-unsplash.jpg",
            "timestamp": datetime.datetime.now(tz=datetime.timezone.utc)
        })
        uposts = ddb.collection("uposts").document(uid).get()
        uposts['f'].append(ddb.collection('post').document(rid))
        ddb.collection("uposts").document(uid).update(uposts)
        ddb.collection("likes").document(rid).set({"a": []})
        ddb.collection("comments").document(rid).set({"c": []})



@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)

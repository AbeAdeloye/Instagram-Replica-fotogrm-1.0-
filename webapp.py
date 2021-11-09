import firebase_admin
import pyrebase
import json
from firebase_admin import credentials, auth
from flask import Flask, request
from functools import wraps
import requests

config = {
    "apiKey": "AIzaSyATS5J03pAt_LJliBweODydObkCpWTuBJc",
    "authDomain": "social-333902.firebaseapp.com",
    "projectId": "social-333902",
    "storageBucket": "social-333902.appspot.com",
    "messagingSenderId": "410902085253",
    "databaseURL":"/",
    "appId": "1:410902085253:web:0cf2c09d952e7eaae2b3ec",
    "measurementId": "G-QXFW1LCKY3"
};

app = Flask(__name__)

cred = credentials.Certificate('keys/firebase.json')
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(config)


@app.route('/signup')
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        return {'message': 'Error missing email or password'}, 400
    try:
        user = auth.create_user(email=email, password=password)
        return {'message': f'Successfully created user {user.uid}'}, 200
    except:
        return {'message': 'Error creating user'}, 400


# Api route to get a new token for a valid user
@app.route('/api/token')
def token():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        jwt = user['idToken']
        return {'token': jwt}, 200
    except:
        return {'message': 'There was an error retrieving your token (user not logged in)'}, 400


def check_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'):
            return {'message': 'No token provided'}, 400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message': 'Invalid token provided.'}, 400
        return f(*args, **kwargs)

    return wrap


if __name__ == '__main__':
    app.run(debug=True)

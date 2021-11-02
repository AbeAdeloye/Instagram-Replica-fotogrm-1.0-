import logging
from flask import Flask, render_template
from google.cloud import datastore
from flask import request
from form import LoginForm
from flask_login import login_user
from models import user

app = Flask(__name__)

@app.route('/')
def home():
    ds = datastore.Client()

    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():


    if form.
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """ 
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)

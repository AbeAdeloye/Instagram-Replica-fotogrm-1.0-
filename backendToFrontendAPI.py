from flask import request


@app.route('/api/signin', methods=["POST","GET"])
def signin():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = auth.sign_in_with_email_and_password(email=email, password=password)
        token = user['idToken']
        return {'token': token}, 200
    except:
        return {'message' : 'There was an error logging in'},400

@app.route('/api/uinfo')

@wrap_token
def uinfo():
    return {'data': users}, 200
def wrap_token(f):
    @wrap f
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'):
            return {'message':'Access token required'}, 400
        try:
            user = auth.verify_id_token(request.headers['authorization'])
            request.user = user
        except:
            return {'message':'Invalid id token'}, 400
        return f(*args **kwargs)
    return wrap
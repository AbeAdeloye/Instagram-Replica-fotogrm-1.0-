from flask_login import login_user
from models import User


@page.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(next=request.args.get('next'))

    if form.validate_on_submit():
        identity = request.form.get('username')
        password = request.form.get('password')

        # fetch user using the 'username' property
        # refer to the datastore-entity documentation for more
        user = User().get_obj('username', identity)

        if user and user.authenticated(password):

            if login_user(user, remember=True):
                user.update_activity()

                # handle optionally redirecting to the next URL safely
                next_url = form.next.data
                if next_url:
                    return redirect(safe_next_url(next_url))

                return redirect(url_for('page/home.html'))
            else:
                flash('This account is not active', 'error')

        else:
            flash('Login or password is incorrect', 'error')

    return render_template("page/login.html", form=form)
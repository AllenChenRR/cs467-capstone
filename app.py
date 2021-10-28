# Code is based off of this google cloud example tutorial.
# https://cloud.google.com/community/tutorials/building-flask-api-with-cloud-firestore-and-deploying-to-cloud-run


# Notes and other useful things
# https://stackoverflow.com/questions/11556958/sending-data-from-html-form-to-a-python-script-in-flask

from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, redirect, request, session, render_template, flash, url_for
import password as pw
import usermodel as model
import traceback
from forms import RegistrationForm, LoginForm

# Initialize Flask app
app = Flask(__name__)

# Set secret key for sessions
app.secret_key = "sdkfjDCVBsdjKkl%@%23$"

# wtf form file
# app.config['SECRET_KEY'] = '1f126886d424206b9b80a69066bf3f8f'

# Initialize Firestore DB
# cred = credentials.Certificate('serviceAccountKey.json')
cred = credentials.Certificate('Key.json') # jamie's db
default_app = initialize_app(cred)
db = firestore.client()


def get_user_id(req):
    """
    Returns the unique ID from a specific document in the users collection or an int if the user is not found.

    """
    user = get_user(req)
    return user if isinstance(user, int) else user.id

def get_user(req):
    """
    Returns the unique user document in the users collection
    """
    user_ref = db.collection('Users')
    query_ref = user_ref.where('email', '==', req['email'])
    all = list(query_ref.stream())
    return len(all) if len(all) != 1 else all[0] 

def get_user_by_email(email):
    """
    Returns the unique user document in the users collection
    """
    user_ref = db.collection('Users')
    query_ref = user_ref.where('email', '==', email)
    all = list(query_ref.stream())
    return len(all) if len(all) != 1 else all[0] 

def validate_user():
    pass

@app.route("/", methods=['GET'])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if the email is already in the database.
            if get_user_by_email(form.email.data):
                flash(f'Email { form.email.data } is already in use.') # borrowed from below...We can change this.
                return render_template("signup.html", title="Sign Up", form=form)

            # Add new user to the database.
            password = form.password.data
            hash_result = pw.return_salt_hash(password) 
            
            request_dict = {
            "first_name": form.first_name.data,
            "last_name": form.last_name.data,
            "email": form.email.data,
            "salt": hash_result[0],
            "hash": hash_result[1],
            "is_admin": False,
            "last_update": datetime.now()}

            user_ref = db.collection('Users')
            user_ref.document().set(request_dict)

            # Logs current user out if new registration occurs
            if 'user' in session:
                session.pop('user', None)

            flash(f'Account created for { form.email.data }', 'success')
            return redirect(url_for('home'))
        
        except Exception as e:
            return f"An Error Occured: {e}"

    return render_template("signup.html", title="Sign Up", form=form)


@app.route('/account', methods=['DELETE', 'POST', 'PATCH'])
def user_account():
    """
    DELETE - Used for testing purposes. Possibly to admins to delete public users.
    Users do not need to be logged in to be deleted.

    """
    # A user does not need to be loged in to have their account deleted.
    if request.method == 'DELETE':
        user_ref = db.collection('Users')
        user_id = get_user_by_email(request.json["email"]).id
        user_ref.document(user_id).delete()
        return "", 204


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        flash(f"Already logged in, {session['user']['first_name']}", 'success')
        if request.referrer is not None:
            return redirect(request.referrer)
        else:
            return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            count = 0
            login_email = form.email.data
            login_user_pw = form.password.data
            users = db.collection('Users').where('email', '==', login_email)\
                                 .stream()
            for user in users:
                count += 1
                user_dict = user.to_dict()
                email = user_dict['email']
                salt = user_dict['salt']
                hash = user_dict['hash']
                first_name = user_dict['first_name']
                last_name = user_dict['last_name']
                is_admin = user_dict['is_admin']
                if pw.is_valid_password(salt, login_user_pw, hash):
                    user_obj = model.User(email, first_name, last_name, 
                                          is_admin)
                    session['user'] = user_obj.__dict__
                    flash(f'Welcome, {first_name}', 'success')
                    return redirect(url_for('home'))
            flash('Login unsuccessful. Please try again.', 'danger')
            return render_template("login.html", title="Login To Your Account", form=form)
        except Exception as e:
            traceback.print_exc()
            # flash('Login unsuccessful. Please try again.', 'danger')
    return render_template("login.html", title="Login To Your Account", form=form)

# Second option for handling log out
@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

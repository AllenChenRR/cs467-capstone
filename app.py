# Code is based off of this google cloud example tutorial.
# https://cloud.google.com/community/tutorials/building-flask-api-with-cloud-firestore-and-deploying-to-cloud-run


# Notes and other useful things
# https://stackoverflow.com/questions/11556958/sending-data-from-html-form-to-a-python-script-in-flask

from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, redirect, request, session, render_template, flash, url_for
from flask.helpers import url_for
import password as pw
import usermodel as model
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


@app.route("/", methods=['GET'])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    user_ref = db.collection('Users')
    if form.validate_on_submit():

        request_dict = {}
        password = form.password.data
        hash_result = pw.return_salt_hash(password) 
        request_dict["first_name"] = form.first_name.data
        request_dict["last_name"] = form.last_name.data
        request_dict["email"] = form.email.data
        request_dict["salt"] = hash_result[0]
        request_dict["hash"] = hash_result[1]
        request_dict["is_admin"] = False
        request_dict["last_update"] = datetime.now()
        
        user_ref.document().set(request_dict)

        flash(f'Account created for { form.email.data }', 'success')
        return redirect(url_for('home'))
    
    return render_template("signup.html", title="Sign Up", form=form)

# ignore this for now...
# # break this up?
# @app.route('/account', methods=['DELETE', 'POST', 'PATCH'])
# def user_account():
#     """
#     Not final but works
#     Does it make sense to have this one route do everything?
#     """
#     try:
#         user_ref = db.collection('users')
#         user_id = get_user_id(request.json)
#         if not isinstance(user_id, int):
#             if request.method == 'POST':
#                 user = user_ref.document(user_id).get()
#                 return jsonify(user.to_dict()), 200
#             if request.method == 'DELETE':
#                 user_ref.document(user_id).delete()
#                 return "", 204
#             # elif request.method == 'PATCH': ### not working yet
#             #     user_ref.document(user_id).update(request.json, merge=True) # need to validate the request json
#                 return "updated", 200
#             else:
#                 return {"error": "Method Not Allowed"}, 405
#         else:
#             if not user_id:
#                 return {"error": "email does not exist"}, 400
#             else:
#                 return {"error": "More than one account with that email"}, 400

#     except Exception as e:
#         return f"An Error Occured: {e}"






# @app.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm()
    
#     if form.validate_on_submit(): # this is checking that the data in the form was valid, hasn't checked against DB yet
#         login_valid = True # this condition can be changed 
#         if login_valid:
#             flash(f'Welcome, {form.email.data}', 'success') # can change to first name later
#             # TODO: You can access the form data with the variables form.email.data 
#             # and form.password.data to check if it's valid, then do whatever you need to do with the DB here
#             return redirect(url_for('home'))
#         else:
#             # in case of an unsuccessful login
#             flash('Login unsuccessful. Please try again.', 'danger')

#     return render_template("login.html", title="Login To Your Account", form=form)


# Handles logging in and logging out
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        auth_object = request.authorization
        login_user_pw = auth_object.password
        login_username = auth_object.username
        users = db.collection('Users').stream()
        for user in users:
            user_dict = user.to_dict()
            username = user_dict['username']
            salt = user_dict['salt']
            hash = user_dict['hash']
            first_name = user_dict['first_name']
            last_name = user_dict['last_name']
            is_admin = user_dict['is_admin']

            if username == login_username:
                if pw.is_valid_password(salt, login_user_pw, hash):
                    user_obj = model.User(username, first_name, last_name,
                                          is_admin)
                    session['user'] = user_obj.__dict__
                return redirect(url_for('home'))
        # Placeholder for handling login failure
        return 'Login Failed'
    # GET - depends if login page is implemented
    else:
        return "Login Page Placeholder"


# Second option for handling log out
@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

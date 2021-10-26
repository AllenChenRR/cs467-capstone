# Code is based off of this google cloud example tutorial.
# https://cloud.google.com/community/tutorials/building-flask-api-with-cloud-firestore-and-deploying-to-cloud-run


# Notes and other useful things
# https://stackoverflow.com/questions/11556958/sending-data-from-html-form-to-a-python-script-in-flask

from datetime import datetime
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, redirect, request, session
from flask.helpers import url_for
import password as pw
import usermodel as model

# Initialize Flask app
app = Flask(__name__)

# Set secret key for sessions
app.secret_key = "sdkfjDCVBsdjKkl%@%23$"

# Initialize Firestore DB
cred = credentials.Certificate('serviceAccountKey.json')
default_app = initialize_app(cred)
db = firestore.client()


def get_user_id(req):
    """
    Returns the unique ID from a specific document in the users collection
    """
    # Create a reference to the users collection
    user_ref = db.collection('users')

    # Query the "users" collection for the document with the matching email
    query_ref = user_ref.where('email', '==', req['email'])
    all = list(query_ref.stream())  # is ther ea better way of doing this?
    if len(all) != 1:
        # something went wrong
        return len(all)
    else:
        # There must be excatly one document in the stream
        # print(all[0].id)
        return all[0].id


@app.route('/', methods=['GET'])
def home():
    """
    Test landing page
    """
    return "This is the landing page for now."


@app.route('/sign_up', methods=['POST'])
def sign_up():  # this could also be used to GET all profiles if we need it

    """
        sign_up() : Add document to Firestore collection with request body.
        e.g. json={
            'first': 'John',
            'last': 'Smith',
            'password': 'abc123'}

        Notes: We could also use a custom ID if needed
    """
    user_ref = db.collection('users')
    if request.method == 'POST':  # will there only be post on the route?
        try:
            request_dict = request.json
            request_dict["admin"] = False
            request_dict["last_update"] = datetime.now()
            user_ref.document().set(request_dict)
            return {"success": True}, 200
        except Exception as e:
            return f"An Error Occured: {e}"
    else:
        return {"error": "Method Not Allowed"}, 405


# break this up?
@app.route('/account', methods=['DELETE', 'POST', 'PATCH'])
def user_account():
    """
    Not final but works
    Does it make sense to have this one route do everything?
    """
    try:
        user_ref = db.collection('users')
        user_id = get_user_id(request.json)
        if not isinstance(user_id, int):
            if request.method == 'POST':
                user = user_ref.document(user_id).get()
                return jsonify(user.to_dict()), 200
            if request.method == 'DELETE':
                user_ref.document(user_id).delete()
                return "", 204
            # elif request.method == 'PATCH': ### not working yet
            #     user_ref.document(user_id).update(request.json, merge=True) # need to validate the request json
                return "updated", 200
            else:
                return {"error": "Method Not Allowed"}, 405
        else:
            if not user_id:
                return {"error": "email does not exist"}, 400
            else:
                return {"error": "More than one account with that email"}, 400

    except Exception as e:
        return f"An Error Occured: {e}"


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

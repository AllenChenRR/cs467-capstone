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
from forms import RegistrationForm, LoginForm, AccountForm

# Initialize Flask app
app = Flask(__name__)

# Set secret key for sessions
app.secret_key = "sdkfjDCVBsdjKkl%@%23$"

# wtf form file
# app.config['SECRET_KEY'] = '1f126886d424206b9b80a69066bf3f8f'

# Initialize Firestore DB
# cred = credentials.Certificate('serviceAccountKey.json')
cred = credentials.Certificate('key.json') # jamie's db
default_app = initialize_app(cred)
db = firestore.client()


####################################################################
# public methods
def get_user_by_email(email):
    """
    Returns a user data dictionary 
    """
    document = _get_document("Users", email=email)
    return _get_document_data(document)

def get_user_by_id(doc_id):
    """
    Returns a user data dictionary 
    """
    document = _get_document("Users", doc_id=doc_id)
    return _get_document_data(document)

def get_salt_and_hash(doc_id):
    """
    Returns document salt and hash values as a tuple.
    """
    doc = get_user_by_id(doc_id)
    return (doc["salt"], doc["hash"])

def add_user(form):
    """
    Adds a new user to the database
    """
    data = _format_user_data(form, new_user=True)
    _set_document("Users", data)

def update_user(form, user_id):
    """
    Updates an existing user in the database
    """
    data = _format_user_data(form, user_id)
    _set_document("Users", data, doc_id=user_id)
    
    # remove salt and hash to update session
    del data['salt']
    del data['hash']
    data['id'] = user_id
    _set_session(data)
#######################################################################
# helper methods
def _get_document(collection, email=None, doc_id=None):
    """
    Returns a collection document or None
    """
    collection_ref = db.collection(collection)
    if email:
        query_ref = collection_ref.where('email', '==', email)
        # There should only be one match
        result_stream = list(query_ref.stream())
        if len(result_stream) == 1:
            return result_stream[0]
    elif doc_id:
        query_ref = collection_ref.document(doc_id)
        if query_ref:
            return query_ref.get()

    return None

def _get_document_data(document):
    """
    Returns a dictionary of the collection document attributes or None.
    """
    document_data = None
    if document:
        document_data = document.to_dict()
        document_data['id'] = document.id
    return document_data

def _format_user_data(form, user_id=None, new_user=False):
    """
    Transforms the form data to a form that can be uploaded to the database
    """
    data = {
        "first_name": form.first_name.data,
        "last_name": form.last_name.data,
        "email": form.email.data,
        "is_admin": False,
        "last_update": datetime.now()}

    if isinstance(form, AccountForm) and form.new_password.data:
        password = form.new_password.data
    else:
        password = form.password.data

    hash_result = pw.return_salt_hash(password) 
    data["salt"] = hash_result[0]
    data["hash"] = hash_result[1]
    return data

def _set_document(collection, data, doc_id=None):
    """
    Add or update collection document in Firestore
    """
    doc_ref = db.collection(collection)
    if doc_id:
        doc_ref.document(doc_id).set(data)
    else:
        doc_ref.document().set(data)

def _set_session(data):
    """
    Updates session data with user data after an update.
    """
    session['user'] = data
#####################################################################

@app.route("/", methods=['GET'])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Add a new user ot the database
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if the email is already in the database.
            if get_user_by_email(form.email.data):
                flash(f'Email { form.email.data } is already in use.')
                return render_template("signup.html", title="Sign Up", form=form)

            # Add a new user to the database.
            add_user(form)

            # Logs current user out if new registration occurs
            if 'user' in session:
                session.pop('user', None)

            flash(f'Account created for { form.email.data }', 'success')
            return redirect(url_for('home'))
        
        except Exception as e:
            return f"An Error Occured: {e}"

    return render_template("signup.html", title="Sign Up", form=form)


@app.route('/account', methods=['POST', 'GET'])
def user_account():
    """
    'GET' - populates Account update form with the current user data from the database
    'POST' - Updates database with all data for the user from the content of the Account update form
    """
    form = AccountForm()
    if request.method == 'GET':
        form.first_name.data = session['user']['first_name']
        form.last_name.data = session['user']['last_name']
        form.email.data = session['user']['email']

    elif request.method == 'POST':
        if form.validate_on_submit():
            user_id = session['user']['id']
            salt, hash = get_salt_and_hash(user_id)
            if pw.is_valid_password(salt, form.password.data, hash):
                update_user(form, user_id)
                flash('Update successful!', 'success')
            else:
                flash('Update unsuccessful. Please try again.', 'danger')
        else:
            flash('Update unsuccessful. Please try again.', 'danger')
    return render_template("account.html", title="Account", form=form)


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
                    session['user']['id'] = user.id 
                    
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
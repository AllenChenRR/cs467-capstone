from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, jsonify, redirect, request, session, render_template, flash, url_for
import helpers as h
import password as pw
import models
import traceback
from forms import EditPetForm, RegistrationForm, LoginForm, AccountForm, AddPetForm
from google.cloud import storage
import os

# Initialize Flask app
app = Flask(__name__)

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="key.json"

# Set secret key for sessions
app.secret_key = "sdkfjDCVBsdjKkl%@%23$"
app.config['BUCKET'] = "cs467-group-app.appspot.com"  # jamies bucket
# app.config['BUCKET'] = 'cs467-capstone-chenall.appspot.com' # Allen's bucket
#app.config['BUCKET'] = "cs-493-assignment-1-327013.appspot.com" # new test bucket

app.config['STORAGE_URL'] = "https://storage.googleapis.com"
app.config['USERS'] = 'Users'
app.config['PETS'] = 'Pets'

# Initialize Firestore DB
# cred = credentials.Certificate('serviceAccountKey.json') # Allen's key
cred = credentials.Certificate('key.json') # jamie's db
# cred = credentials.Certificate('testDeployKey.json') # jamie's db
default_app = initialize_app(cred)
db = firestore.client()
storage_client = storage.Client()
bucket = storage_client.bucket(app.config['BUCKET'])
DISPOSITIONS = ["good with children", "good with other animals",
                "animal must be leashed at all times"]
CAT_BREEDS = [("maine coon", "Maine Coon"), ("siamese", "Siamese"), ("american shorthair", "American Shorthair"), 
                ("tabby", "Tabby"), ("other", "Other")]
DOG_BREEDS = [("golden retriever", "Golden Retriever"), ("german shepherd", "German Shepherd"), ("bulldog", "Bulldog"), ("other", "Other")]
OTHER_BREEDS = [("other", "Other")]
ANIM_TYPES = [("cat", "Cat"), ("dog", "Dog"), ("other", "Other")]
AVAILABILITIES = [('available', 'Available'), ('pending', 'Pending'), ('adopted', 'Adopted')]


@app.route("/", methods=['GET'])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Add a new user to the database
    """
        # Logs current user out if new registration occurs
    if 'user' in session:
        error_message = "You are already logged in. Please log out first to create a new account."
        return render_template("error.html", error_message=error_message)

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if the email is already in the database.
            if h.get_user_by_email(db, form.email.data):
                flash(f'Email { form.email.data } is already in use.', 'danger')
                return render_template("signup.html", title="Sign Up", form=form)

            # Add a new user to the database.
            h.add_user(db, form)
            # Login the user after they are registered in the database
            users = db.collection('Users').where('email', '==', form.email.data)\
                                 .stream()
            for user in users:
                user_dict = user.to_dict()
                if pw.is_valid_password(user_dict['salt'], form.password.data, 
                                        user_dict['hash']):
                    user_obj = models.User(user_dict['email'], 
                                           user_dict['first_name'], 
                                           user_dict['last_name'],
                                           user_dict['is_admin'])
                    session['user'] = user_obj.__dict__
                    session['user']['id'] = user.id

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
        try:
            if form.validate_on_submit():
                user_id = session['user']['id']

                # Check if the email is already in use
                user = h.get_user_by_email(db, form.email.data)
                if user and user["id"] != user_id:
                    flash(f'Email { form.email.data } is already in use.', 'danger')
                    return redirect('/account')

                salt, hash = h.get_salt_and_hash(db, user_id)
                if pw.is_valid_password(salt, form.password.data, hash):
                    h.update_user(db, form, user_id)
                    flash('Update successful!', 'success')
                else:
                    flash('Invalid password. Please try again.', 'danger')
            else:
                flash('Update unsuccessful. Please try again.', 'danger')
        except Exception as e:
            return f"An Error Occured: {e}"
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
            login_email = form.email.data
            login_user_pw = form.password.data
            users = db.collection('Users').where('email', '==', login_email).stream()
            for user in users:
                user_dict = user.to_dict()
                first_name = user_dict['first_name']
                if pw.is_valid_password(user_dict['salt'], login_user_pw, 
                                        user_dict['hash']):
                    user_obj = models.User(user_dict['email'],
                                           user_dict['first_name'],
                                           user_dict['last_name'],
                                           user_dict['is_admin'])
                    session['user'] = user_obj.__dict__
                    session['user']['id'] = user.id
                    flash(f'Welcome, {first_name}', 'success')
                    return redirect(url_for('home'))
            flash('Login unsuccessful. Please try again.', 'danger')
            return render_template("login.html", title="Login To Your Account",
                                   form=form)
        except Exception as e:
            traceback.print_exc()
    return render_template("login.html", title="Login To Your Account",
                           form=form)

# Second option for handling log out
@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/browse-pets', methods=['GET'])
def browse_pets():
    
    # pet_type will come from a form. It will be dog, cat, other or None. 
    # If it is None, all pets will be returned.
    pet_type = None

    pets = h.browse_pets(db, pet_type)
    if not pets:
        pets = [f"Sorry, there are no {pet_type}s to display"]
    return render_template('browse-pets.html', title="Browse Available Pets", pets=pets)


@app.route('/add-pet', methods=['GET', 'POST'])
def add_pet():
    """
    Adds a new pet to the database.
    """
    form = AddPetForm()
    if request.method == "POST":
        form.breed.choices = h.return_breed_choices(form.breed.data, 
                                            form.animal_type.data)
        if form.validate_on_submit():
            pet_id = h.add_new_pet(db, form)
            h.update_pet_image(app, db, pet_id)
            # creates a blob with pet_id as the name
            blob = bucket.blob(pet_id)
            blob.upload_from_file(form.image.data, rewind=True,
                                  content_type='image/jpeg')
            blob.make_public()
            # Prevents double post problem
            flash(f'Pet {form.name.data} added successfully', 'success')
            return redirect(url_for("add_pet"))
        else:
            print(f'Form errors: {form.errors}')
    return render_template('add-pet.html', title="Add a Pet to the Shelter", form=form)


@app.route('/pets/<id>', methods=['GET', 'DELETE'])
def get_pet(id):
    # I changed the name of this since it was the same as a helper function
    if request.method == "GET":
        pet_data = h.get_pet_by_id(db, id)
        if not pet_data:
            return render_template('does-not-exist.html')
    elif request.method == "DELETE":
        h.delete_pet(db, id)
        return render_template('does-not-exist.html')
    elif request.method == "POST":
        # update pet
        pass

    return render_template('pet-profile.html', pet_data=pet_data)


@app.route('/search', methods=['GET', 'POST'])
def search():
    h.search_pets(db, {})
    return "", 200


@app.route('/pets/<id>/edit', methods=['GET', 'POST'])
def edit_pet_by_id(id):
    pet_data = h.get_pet_by_id(db, id)
    if pet_data is None:
        error_message = "Pet not found"
        return render_template("error.html", error_message=error_message), 404

    form = EditPetForm()
    # Changes the choices to match current pet
    form.animal_type.choices = h.create_default_list(pet_data['animal_type'], ANIM_TYPES)
    form.availability.choices = h.create_default_list(pet_data['availability'], AVAILABILITIES)
    form.breed.choices = h.return_breed_choices(pet_data["breed"], pet_data["animal_type"])

    if request.method == 'GET':
        form = h.populate_pet_form(form, pet_data)
    elif request.method == 'POST':
        try:
            # Updates form breed choices to reflect change on client side
            form.breed.choices = h.return_breed_choices(form.breed.data, 
                                                        form.animal_type.data)
            if form.validate_on_submit():
                h.update_pet(db, form, id)
                if form.image.data is not None:
                    h.update_pet_image(app, db, id)
                    blob = bucket.blob(id)
                    blob.upload_from_file(form.image.data, rewind=True,
                                    content_type='image/jpeg')
                    blob.make_public()
                flash(f'Pet {form.name.data} updated successfully', 'success')
                return redirect(url_for("edit_pet_by_id", id=id))
        except Exception as e:
            traceback.print_exc()
    return render_template('edit-pet.html', title="Update pet content",
                           pet_data=pet_data, form=form)


# Handles generating breed choices based on animal type
@app.route('/type/<get_breed_by_type>')
def get_breed(get_breed_by_type):
    if get_breed_by_type.lower() == "cat":
        return jsonify(CAT_BREEDS)
    elif get_breed_by_type.lower() == "dog":
        return jsonify(DOG_BREEDS)
    elif get_breed_by_type.lower() == "other":
        return jsonify(OTHER_BREEDS)
    else:
        error_message = "Type not found"
        return render_template("error.html", error_message=error_message), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)






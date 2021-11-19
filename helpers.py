from datetime import datetime
import os

from flask import session
from forms import AccountForm

import helpers as h
import password as pw

CAT_BREEDS = [("maine coon", "Maine Coon"), ("siamese", "Siamese"), ("other", "Other")]
DOG_BREEDS = [("retriever", "Retriever"), ("bulldog", "Bulldog"), ("other", "Other")]
OTHER_BREEDS = [("other", "Other")]


def update_pet(db, form, pet_id):
    data = _format_pet_data(form)
    _set_document(db, "Pets", data, doc_id=pet_id, merge=True)


def create_default_list(default:str,
                        arr: "list[tuple(str, str)]"
                        ) -> "list[tuple(str, str)]":
    """Creates a new form field choices list with default value as first element
    """
    for i in range(len(arr)):
        if default.lower() == arr[i][0]:
            arr.insert(0, arr.pop(i))
            return arr
    
def populate_pet_form(form, pet_data):
    form.name.data =pet_data["name"]
    form.animal_type.data = pet_data["animal_type"]
    form.breed.data = pet_data["breed"]
    form.availability.data = pet_data["availability"]
    form.disposition.data = pet_data["disposition"]
    form.description.data = pet_data["description"]
    return form

def return_breed_choices(breed:str, type:str) -> "list[tuple(str, str)]":
    """Returns breed choices based on animal type
    """
    if type.lower() == "cat":
        return create_default_list(breed, CAT_BREEDS)
    elif type.lower() == "dog":
        return create_default_list(breed, DOG_BREEDS)
    elif type.lower() == "other":
        return create_default_list(breed, OTHER_BREEDS)
    else:
        return None

def get_image_url(app, id):
    return os.path.join(
        app.config['STORAGE_URL'],
        app.config['BUCKET'],
        id
    )

def add_new_pet(db, form):
    """
    Adds a new pet to the database
    """
    data = _format_pet_data(form)
    data['date_created'] =  datetime.now()
    return _add_document(db, "Pets", data)


def update_pet_image(app, db, pet_id):
    """
    Updates the image attribute of an existing pet in the database
    """
    data = {"image": h.get_image_url(app, pet_id)}
    _set_document(db, "Pets", data, doc_id=pet_id, merge=True)


def get_pet_by_id(db, doc_id):
    """
    Returns a pet data dictionary 
    """
    document = _get_document(db, "Pets", doc_id=doc_id)
    return _get_document_data(document)

def browse_pets(db, pet_type=None):
    """
    Returns a list of dictionaries, one per pet for the given pet_type.
    If no pet_type is given, it will returns a list of dictionaries, 
    one per pet for all pets in the database.
    """
    query = None
    pets_list = []
    pets = db.collection("Pets")
    
    if pet_type:
        query = pets.where("animal_type", "==", pet_type)
        
    if query:  
        pets_list = list(query.stream())
    else:
        pets_list =  list(pets.stream())

    pet_data = list(map(_get_document_data, pets_list))
    pet_data.sort(key=lambda x: x["date_created"], reverse=True)
    return pet_data

def search_pets(db, attribute_dict):
    # attribute_dict will be a form
    # TODO create a function reads a form and puts it into a dict
    attribute_dict = {"name": "The Notorious P.I.G."}
    pets_ref = db.collection("Pets")
    pets_query = ["pets_ref"]
    for k, v in attribute_dict.items():
        pets_query.append(f".where('{k}', '==', '{v}')")
    pets_query_str = "".join(pets_query)
    result = eval(pets_query_str)
    for match in result.stream():
        print(match.id)


def delete_pet(db, pet_id):
    """ 
    Deletes an animal's data from the database
    """
    db.collection("Pets").document(pet_id).delete()

def get_user_by_email(db, email):
    """
    Returns a user data dictionary 
    """
    document = _get_document(db, "Users", email=email)
    return _get_document_data(document)

def get_user_by_id(db, doc_id):
    """
    Returns a user data dictionary 
    """
    document = _get_document(db, "Users", doc_id=doc_id)
    return _get_document_data(document)

def get_salt_and_hash(db, doc_id):
    """
    Returns document salt and hash values as a tuple.
    """
    doc = get_user_by_id(db, doc_id)
    return (doc["salt"], doc["hash"])

def add_user(db, form):
    """
    Adds a new user to the database
    """
    data = _format_user_data(form, new_user=True)
    _set_document(db, "Users", data)

def update_user(db, form, user_id):
    """
    Updates an existing user in the database
    """
    data = _format_user_data(form, user_id)
    _set_document(db, "Users", data, doc_id=user_id)
    
    # remove salt and hash to update session
    del data['salt']
    del data['hash']
    data['id'] = user_id
    _set_session(data)
#######################################################################
# helper methods
def _get_document(db, collection, email=None, doc_id=None):
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
    if document and document.exists:
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

def _set_document(db, collection, data, doc_id=None, merge=False):
    """
    Add or update collection document in Firestore
    """
    
    doc_ref = db.collection(collection)
    if doc_id and merge:
        doc_ref.document(doc_id).set(data, merge=True)
    elif doc_id:
        doc_ref.document(doc_id).set(data)
    else:
        doc_ref.document().set(data)

def _set_session(data):
    """
    Updates session data with user data after an update.
    """
    session['user'] = data

def _format_pet_data(form):
    """
    Transforms the form data to a form that can be uploaded to the database
    """
    data = {
        "name": form.name.data,
        "animal_type": form.animal_type.data,
        "breed": form.breed.data,
        "disposition": form.disposition.data,
        "availability": form.availability.data,
        "description": form.description.data,
        "last_update": datetime.now(),
    }

    return data

def _add_document(db, collection, data):
    """
    Add collection document in Firestore
    """
    doc_ref = db.collection(collection).add(data)
    return doc_ref[1].id
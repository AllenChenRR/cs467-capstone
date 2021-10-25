import hashlib
import random
import string
from datetime import datetime


def _create_salt(length):
    """Returns a randomly generated string that contains alphanumeric characters
        of specified length"
    """
    random.seed(datetime.now())
    return ''.join(random.choices(string.ascii_letters + string.digits,
                                  k=length))


def return_salt_hash(password):
    """Returns the salt and hash value of the salted password

    Args:
        password (string): Password from user when creating account

    Returns:
        tuple: A 2-tuple that contains the salt and hash respectively
    """
    size = 32
    salt = _create_salt(size)
    hash_obj = hashlib.sha256(password.encode() + salt.encode())
    hashed = hash_obj.hexdigest()
    return (salt, hashed)


def is_valid_password(salt, password, hash):
    """ Determines if password is valid

    Args:
        salt (string): The salt associated with user
        password (string): Password from user logging in
        hash (string): Hash associated with user

    Returns:
        Returns a true if password is valid, otherwise returns false
    """
    hash_obj = hashlib.sha256(password.encode() + salt.encode())
    hashed = hash_obj.hexdigest()
    return hashed == hash
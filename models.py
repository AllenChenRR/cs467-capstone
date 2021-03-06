import datetime
import os

class User():
    def __init__(self, email: str,
                 first_name: str,
                 last_name: str,
                 is_admin=False):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin

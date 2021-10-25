class User():
    def __init__(self, username: str,
                 firstName: str,
                 lastName: str,
                 isAdmin=False):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.isAdmin = isAdmin

class TestUser():
    def __init__(self, username='testing username'):
        self.username = username

'''Module that contains the class to create accounts.'''
class Account:
    '''A class that represents a user account.

    Attributes:
        username (string): The name of the account.
        password (string): The password of the account.
    '''
    def __init__(self,
                 username,
                 password):
        '''Constructor for the account class.

        Args:
            username (string): The name of the account.
            password (string): The password of the account.
        '''
        if not isinstance(username, str):
            raise TypeError("The username is not a string")
        if not isinstance(password, str):
            raise TypeError("The password is not a string")
        self.username = username
        self.password = password

# In-memory user credentials (change to database-based in production)
users = {'admin': 'password123', 'user': 'userpassword'}

def check_user_credentials(username, password):
    """
    Simple function to check if the username and password are correct.
    Replace this with a more secure authentication method in production.
    """
    return users.get(username) == password

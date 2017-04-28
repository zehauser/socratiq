import os

def running_in_production():
    return os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/')
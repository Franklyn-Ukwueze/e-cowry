import os

base_dir = os.path.abspath(os.path.dirname(__file__))

#create configuration class
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')

MONGO_URI = os.getenv("MONGO_URI")
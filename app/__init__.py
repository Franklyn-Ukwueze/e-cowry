import os
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_cors import CORS
from pymongo import MongoClient
from app.config import Config, MONGO_URI
#from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
#load_dotenv(os.path.join(basedir, '.env'))



# from flask_pymongo import PyMongo

# Initialize application
app = Flask(__name__)

# app configuration
app.config.from_object(Config)

# Initialize Flask Api
api = Api(app)

CORS(app)
#Initialize db
client = MongoClient(os.getenv("MONGO_URI"))
db = client.cowry

# Import the application webservice
from app import api, work ,error
import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Connect to the database

class Config:
    database_name = "fyyurapp"
    username = 'postgres'
    password = 'sliman17'
    url = 'localhost:5432'

    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        username, password, url, database_name)
    SECRET_KEY = os.urandom(32)
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

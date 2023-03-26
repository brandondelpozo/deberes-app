import sqlite3

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create the Flask app instance
app = Flask(__name__)
# set the secret key for the app
app.config['SECRET_KEY'] = os.urandom(32)
# configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
# initialize the database with the app
db = SQLAlchemy(app)
# import views and models
from . import views, models

# wrap the database initialization in an application context
with app.app_context():
    # create the database tables
    db.create_all()

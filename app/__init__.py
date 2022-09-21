from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = 'SECRET_KEY'


from app import views
from app import models

db.init_app(app)
db.create_all()
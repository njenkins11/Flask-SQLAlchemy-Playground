from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

# Important docs: https://flask-sqlalchemy.palletsprojects.com/en/2.x/index.html

# Instantiate flask app
app = Flask(__name__)

# Have to have config before instantiating SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Prevents SQLAlchemy from showing errors when changing items
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' # Location or URL for database

# Instantiate DB object
db = SQLAlchemy(app)

# Each class represents a table within SQLite
# Inheriting from the DB object above (db) then .model, since this is a model.
class User(db.Model):
    # Every model must have a PK / ID
    id = db.Column(db.Integer, primary_key = True) # Parameters sets the data type for inside the db, as well as any other settings such as PK or increment
    name = db.Column(db.String(50)) # The 50 within String(50) is the string length.
    location = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.now) # Default is the default time. The datetime.now is a function which will be called when the row is created.

# Database and Tables can be created with SQLAlchemy
# By running 'from app import db'
# 'db.create_all()

# Creates a route and defines any parameters for the url.
# The method after that defines what to do with that information. In this case, it creates the user.
@app.route('/<name>/<location>')
def index(name, location):
    user = User(name=name, location=location)
    db.session.add(user)
    db.session.commit()

    return '<h1>Added New User!</h1>'

# Queries to find the correct name. The left hand side is the column name, and the right hand side is the parameter.
# It will filter out the User table object from the name
@app.route('/<name>')
def get_user(name):
    user = User.query.filter_by(name=name).first() # .first will only show the first result for the query. '.all' will show every result.
    
    if user: # If the user is found, then the location will be printed. Else, it will display a warning to prevent an internal server error.
        return f'<h1> The user\'s is located in: {user.location} </h1>' # This will return the user's location based on the search above.
    else:
        return '<h1> Invalid name. </h1>' # If the name is not found
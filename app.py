from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

# Important docs: https://flask-sqlalchemy.palletsprojects.com/en/2.x/index.html
# Filter docs: https://docs.sqlalchemy.org/en/14/orm/tutorial.html#common-filter-operators

PAGE_SIZE = 10 # For pagination

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
def add_user(name, location):
    user = User(name=name, location=location)
    db.session.add(user)
    db.session.commit()

    return '<h1>Added New User!</h1>'

# Queries to find the correct name. The left hand side is the column name, and the right hand side is the parameter.
# It will filter out the User table object from the name
@app.route('/user/<int:id>')
def get_user(id):
    user = User.query.get(id) # Gets the user by the PK, or id in this case
    
    if user: # If the user is found, then this user's info will be printed. Else, it will display a warning to prevent an internal server error.
        return render_template('user.html', user=user) # This will return the user's info based on the search above to the template (for user var) for rendering.
    else:
        return '<h1> Invalid ID. </h1>' # If the name is not found

# Searches for like terms. Example: Search "n" and one results may be 'Nicole'
@app.route('/search/name=<name>')
def search_user(name):
    user = User.query.filter(User.name.like('%'+name+'%')).first() # 'like' searches for like terms. The 'first' is, once again, only showing the first result.
    # If user -> show user name, if not then show error.
    if user:
        return f'<h1> First result of search: {user.name} </h1>'
    else:
        return f'<h1> Could not find user. </h1>'

@app.route('/search/location=<location>')
def search_location(location):
    user = User.query.filter(User.location.like('%'+location+'%')).first()

    if user:
        return f'<h1> User with this location is: {user.name} </h1>'
    else:
        return f'<h1> Could not find user based on location. </h1>'

@app.route('/search-list/name=<name>')
def search_users(name):
    users = User.query.filter(User.name.like('%'+name+'%')) # Gets ALL of the similar names to this given name.
    # Loop through results if found
    # Pagination will probably be needed w/ more data in db
    result = ""

    if users:
        for user in users:
            result += f'<h1><li>Name: {user.name} \t Location: {user.location}</li></h1>'
        return result
    else:
        return f'<h1> Could not find user. </h1>'

@app.route('/<int:page>')
def index(page=1):
    users = User.query.order_by(User.id).paginate(page,PAGE_SIZE,error_out=False) # Pagination!!!
    return render_template("index.html", users=users) # Returns users to allow HTML to loop through the users for this current page

# Redirects to the index page above
# Everyone must see the list mahaahahwa!!!
@app.route('/')
def redirect_index():
    return redirect(url_for('index', page=1))
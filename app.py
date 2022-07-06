from venv import create
from flask import Flask, flash, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

# Important docs: https://flask-sqlalchemy.palletsprojects.com/en/2.x/index.html
# Queries: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
# Filter docs: https://docs.sqlalchemy.org/en/14/orm/tutorial.html#common-filter-operators

PAGE_SIZE = 10 # For pagination

# Instantiate flask app
app = Flask(__name__)

# Have to have config before instantiating SQLAlchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Prevents SQLAlchemy from showing errors when changing items
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' # Location or URL for database
app.config['SECRET_KEY'] = '2t3wlekgj203520523wslkd20358269243'

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
    audit = db.relationship("Audit")

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, default=datetime.now)
    message = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

# Database and Tables can be created with SQLAlchemy
# By running 'from app import db'
# 'db.create_all()

# Queries to find the correct name. The left hand side is the column name, and the right hand side is the parameter.
# It will filter out the User table object from the name
@app.route('/user/<int:id>')
def get_user(id):
    user = User.query.get(id) # Gets the user by the PK, or id in this case
    
    if user: # If the user is found, then this user's info will be printed. Else, it will display a warning to prevent an internal server error.
        return render_template('user.html', user=user) # This will return the user's info based on the search above to the template (for user var) for rendering.
    else:
        return '<h1> Invalid ID. </h1>' # If the name is not found

@app.route('/audit/<int:id>')
def get_audit(id):
    audit = Audit.query.get(id)

    if audit:
        return '<h1> {{audit.message}} </h1>'
    else:
        return '<h1> Invalid Audit </h1>'

# Home page
@app.route('/users=<int:page>/audits=<int:audit_page>', methods=('GET', 'POST'))
def index(page=1, audit_page=1):
    users = User.query.order_by(User.id).paginate(page,PAGE_SIZE,error_out=False) # Pagination!!!
    audits = Audit.query.order_by(Audit.date).paginate(audit_page,PAGE_SIZE, error_out=False)

    # If it is a post request, filter through the db and re-render the website with the new users.
    if request.method == 'POST':
        search_name = request.form['name']
        if search_name:
            users = User.query.filter(User.name.like('%'+search_name+'%')).paginate(page,PAGE_SIZE,error_out=False)
    return render_template("index.html", users=users, audits=audits) # Returns users to allow HTML to loop through the users for this current page

# Redirects to the index page above
# Everyone must see the list mahaahahwa!!!
@app.route('/')
def redirect_index():
    return redirect(url_for('index', page=1, audit_page=1))

# Create user form
@app.route('/create/', methods=('GET', 'POST')) # Have to get the information from the user to fill out a user row in the db.
def create_user():
    if request.method == 'POST':
        name = request.form['name'] # Gets the information from the create.html. The variables are assigned in that form.
        location = request.form['location']
        # Checks to see if the form has been filled out. If not, it will send the user a warning
        if not name:
            flash('Name is required')
        elif not location:
            flash('Location is required')
        else:
            # After checks, it will send the information to the db, then redirect this user to the home page.
            user = User(name=name,location=location)
            message = f"Created user {user.name}."
            create_audit(user.id, message)
            db.session.add(user)
            db.session.commit()
            flash('Sucess!')
            return redirect(url_for('index',page=1))
    return render_template('create.html')

# Simply kills--- Deletes* the user
@app.route('/delete/<int:id>')
def delete_user(id):
    user = User.query.get(id)
    if user:
        message = f"Deleted {user.name} with an ID of {user.id}."
        create_audit(id,message)
        db.session.delete(user)
        db.session.commit()
    
    return redirect(url_for('index',page=1))

# Updates the user based on information.
@app.route('/update/<int:id>', methods=('GET', 'POST'))
def update_user(id):
    user = User.query.get(id)
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        audit = ""

        # If there is a name or a location, that means the user wants to change it
        if name:
            audit += f"Changed from {user.name} to {name}."
            user.name = name
        if location:
            audit += f"Changed {user.name}'s location from {user.location} to {location}."
            user.location = location
        
        # Updates the user by readding it. As long as it has the same id, it will update the user with that specific id, like in Spring Hibernate.
        create_audit(id,audit)
        db.session.add(user)
        db.session.commit()
        # Redirects if the request is a POST
        return redirect(url_for('index',page=1))
    # Returns render if it was a GET request
    return render_template('update.html', user=user)

@app.route('/delete/<int:id>/confirm')
def confirm_delete(id):
    user = User.query.get(id)
    return render_template('confirm.html', user=user)

def create_audit(id, message):
    audit = Audit(user_id=id, message=message)
    db.session.add(audit)
    db.session.commit()

# NOTESSSSS

# Creates a route and defines any parameters for the url.
# The method after that defines what to do with that information. In this case, it creates the user.
@app.route('/<name>/<location>')
def add_user(name, location):
    user = User(name=name, location=location)
    db.session.add(user)
    db.session.commit()

    return '<h1>Added New User!</h1>'

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




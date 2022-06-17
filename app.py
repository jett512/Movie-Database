from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

import re
import sqlite3
import os.path
import json

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'Flask%Crud#Application'

app.permanent_session_lifetime = timedelta(minutes=5)


# Enter your database connection details below
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "db.sqlite")
movies_path = os.path.join(BASE_DIR, "static/movies.json")
f = open(movies_path, encoding="utf8")
Movies = json.loads(f.read())

#SqLite database connection
conn = sqlite3.connect(db_path, check_same_thread=False)


@app.route('/', methods=['GET', 'POST'])
def cover():
    # Open sqlite database connection
    cursor = conn.cursor()

    # Drop existing movies table in the database
    cursor.execute('DROP TABLE movies')

    # Create a new movies table to load updated movies
    cursor.execute('CREATE TABLE movies(Title TEXT, Year INTEGER, Cast TEXT, Genres TEXT)')

    # Sort the movies list according to the year - latest to oldest
    sorted_list = sorted(Movies, key=lambda sort: sort['year'], reverse=True)

    # Loop through first 1000 movies
    for i in range(1000):
        # Get each movie which is a dictionary
        mov = sorted_list[i]

        # Regular expression to keep only letters, numbers and , in a movie cast while replacing everything else with a space " "
        cast_trim = re.sub('[^a-zA-Z0-9 , \n\.]', '', str(mov['cast']))

        # Regular expression to keep only letters, numbers and , in a movie genres while replacing everything else with a space " "
        genres_trim = re.sub('[^a-zA-Z0-9 , \n\.]', '', str(mov['genres']))

        # Insert movie information into movie table
        cursor.execute('INSERT INTO movies (Title, Year, Cast, Genres) VALUES (?, ?, ?, ?)',
                       (mov['title'], mov['year'], cast_trim, genres_trim,))

    # Confirm insertion and close database connection
    conn.commit()


    # Display the cover page
    return render_template('cover.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for("home"))

    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        session.permanent = True

        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

        # Fetch one record and return result
        user = cursor.fetchone()

        # If user exists in users table in the database
        if user and check_password_hash(user[4], password):

            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['firstname'] = user[0]
            session['username'] = user[3]

            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # user doesnt exist or username/password incorrect
            msg = 'Incorrect username/password! :/'

    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('firstname', None)
    session.pop('username', None)

    # Redirect to login page
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        # Create variables for easy access
        first = request.form['firstname']
        last = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hash = generate_password_hash(password)
        email = request.form['email']

        # Check if user exists using MySQL
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))   #SqLite Connect statement
        user = cursor.fetchone()

        # If user exists show error and validation checks
        if user:
            msg = 'Username/user already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # user doesnt exists and the form data is valid, now insert new user into users table
            # SqLite Insert Statement
            cursor.execute('INSERT INTO users (firstname, lastname, email, username, password) VALUES (?, ?, ?, ?, ?)',
                           (first, last, email, username, hash,))
            conn.commit()
            msg = 'You have successfully registered!'
            return render_template('index.html')

    elif request.method == "POST":
        # Form is empty... (no POST data)
        msg = 'Please fill all required fields!'

    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


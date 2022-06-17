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
            session['searches'] = ""

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


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # Initialize a list to store 100 movies of each category
        display_list = [ ]

        # Open database connection
        cursor = conn.cursor()
        # create table for user with amount of movies watched in categories
        sql_drop = """SELECT name FROM sqlite_master WHERE type='table'
          AND name='""" + session['username'] + "';"
        tableList = cursor.execute(sql_drop).fetchall()
        if tableList == []:
            sql = 'CREATE TABLE ' + session[
                'username'] + '(Action INTEGER, Drama INTEGER, Thriller INTEGER, Comedy INTEGER)'
            cursor.execute(sql)
            sql2 = 'INSERT INTO ' + session['username'] + ' VALUES (0, 0, 0, 0)'
            cursor.execute(sql2)
            conn.commit()

        #create search history table for user
        sql_drop = """SELECT name FROM sqlite_master WHERE type='table'
                  AND name='""" + session['username'] + "search';"
        tableList = cursor.execute(sql_drop).fetchall()
        if tableList == []:
            sql = 'CREATE TABLE ' + session[
                'username'] + 'search(searches TEXT)'
            cursor.execute(sql)


        # Initialize a list of categories
        genres_words = ['Action', 'Drama', 'Thriller', 'Comedy']

        # Loop through each category
        for j in range(len(genres_words)):
            # SQL query to extract movies of each category
            word = '%' + genres_words[j] + '%'
            cursor.execute('SELECT * FROM movies WHERE Genres LIKE ?', [word])

            # Fetch movies of each category and return result
            movies_list = cursor.fetchall()
            list_length = len(movies_list)

            # Temporary list to contain 100 movies of a category
            temp_list = []

            # Append category word into the list
            temp_list.append(genres_words[j])

            # Check if there are 100 movies in a category
            if list_length > 100:
                # Loop through each movie and append to the temporary list
                for k in range(100):
                    temp_list.append(movies_list[k])
                # Append the temporary list to the main list
                display_list.append(temp_list)
            else:
                for k in range(list_length):
                    temp_list.append(movies_list[k])
                display_list.append(temp_list)

        # User is loggedin show them the home page
        return render_template('home.html', movies=json.dumps(display_list), num_categories=len(genres_words), categories=genres_words, username=session['username'], searchedMovies=session['searches'])

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the user info for the user so we can display it on the profile page
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (session['username'],))
        user = cursor.fetchone()
        sql = 'SELECT * FROM ' + session['username']
        cursor.execute(sql)
        movieCount = cursor.fetchone()

        sql = 'SELECT * FROM ' + session['username'] + 'search'
        cursor.execute(sql)
        history = cursor.fetchall()

        # Show the profile page with user info
        return render_template('profile.html', user=user, movieCount=movieCount, history=history)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/actionTask')
def actionTask():
    cursor = conn.cursor()
    sql = 'SELECT Action FROM ' + session['username']
    cursor.execute(sql)  # SqLite Connect statement
    Count = cursor.fetchone()
    Count_trim = re.sub('[^0-9 , \n\.]', '', str(Count))
    Count_trim = Count_trim.replace(",", "")
    update = int(Count_trim) + 1
    sql2 = "UPDATE " + session['username'] + " SET Action = " + str(update) + " WHERE Action = " + str(Count_trim)
    cursor.execute(sql2)
    conn.commit()
    return redirect(url_for('home'))

@app.route('/thrillerTask')
def thrillerTask():
    cursor = conn.cursor()
    sql = 'SELECT Thriller FROM ' + session['username']
    cursor.execute(sql)  # SqLite Connect statement
    Count = cursor.fetchone()
    Count_trim = re.sub('[^0-9 , \n\.]', '', str(Count))
    Count_trim = Count_trim.replace(",", "")
    update = int(Count_trim) + 1
    sql2 = "UPDATE " + session['username'] + " SET Thriller = " + str(update) + " WHERE Thriller = " + str(Count_trim)
    cursor.execute(sql2)
    conn.commit()
    return redirect(url_for('home'))

@app.route('/dramaTask')
def dramaTask():
    cursor = conn.cursor()
    sql = 'SELECT Drama FROM ' + session['username']
    cursor.execute(sql)  # SqLite Connect statement
    Count = cursor.fetchone()
    Count_trim = re.sub('[^0-9 , \n\.]', '', str(Count))
    Count_trim = Count_trim.replace(",", "")
    update = int(Count_trim) + 1
    sql2 = "UPDATE " + session['username'] + " SET Drama = " + str(update) + " WHERE Drama = " + str(Count_trim)
    cursor.execute(sql2)
    conn.commit()
    return redirect(url_for('home'))

@app.route('/comedyTask')
def comedyTask():
    cursor = conn.cursor()
    sql = 'SELECT Comedy FROM ' + session['username']
    cursor.execute(sql)  # SqLite Connect statement
    Count = cursor.fetchone()
    Count_trim = re.sub('[^0-9 , \n\.]', '', str(Count))
    Count_trim = Count_trim.replace(",", "")
    update = int(Count_trim) + 1
    sql2 = "UPDATE " + session['username'] + " SET Comedy = " + str(update) + " WHERE Comedy = " + str(Count_trim)
    cursor.execute(sql2)
    conn.commit()
    return redirect(url_for('home'))

@app.route('/search', methods =["GET", "POST"])
def search():
    if request.method == "POST":
        searchInput = request.form.get("searcher")
        cursor = conn.cursor()
        sql2 = 'INSERT INTO ' + session['username'] + 'search VALUES ("' + searchInput + '")'
        cursor.execute(sql2)
        conn.commit()
        variable = "'%" + searchInput + "%'"
        sql = "SELECT Title FROM movies WHERE Title LIKE " + variable
        cursor.execute(sql)
        searchedMovies = cursor.fetchall()
        session['searches'] = searchedMovies
        return redirect(url_for('home'))

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()

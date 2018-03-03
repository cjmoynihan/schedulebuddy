__author__ = 'cj'
"""
Handles the actual server handling for Flask
"""
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import data_handling as db

app = Flask(__name__)

app.config.from_object(__name__)  # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# The database interfacing
def get_db():
    """
    Get's a new database connection once the context is broken
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = db.Database()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """
    Closes the connection to reduce open threads in between web calls
    """
    get_db().conn.close()

# Actual web handling
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['action'] == 'Login':
            if request.form['username'] not in get_db().c.execute("SELECT username FROM users").fetchall():
                error = 'Invalid username'
            elif request.form['password'] not in get_db().c.execute("SELECT password FROM users").fetchall():
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                flash('You were logged in')
                return redirect(url_for('show_calendar'))
        elif request.form['action'] == 'Add User':
            if request.form['username'] in get_db().c.execute("SELECT username FROM users").fetchall():
                error = 'Invalid username'
            else:
                get_db().add_user(request.form['username'], request.form['password'])
                session['logged_in'] = True
                flash('User added. You were logged in')
                return redirect(url_for('show_calendar'))
        return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/show_calendar')
def show_calendar():
    return "Hello World! We did it!"

# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     db = get_db()
#     db.execute('insert into entries (title, text) values (?, ?)',
#                  [request.form['title'], request.form['text']])
#     db.commit()
#     flash('New entry was successfully posted')
#     return redirect(url_for('show_entries'))

# @app.route('/')
# def show_entries():
#     db = get_db()
#     cur = db.execute('select title, text from entries order by id desc')
#     entries = cur.fetchall()
#     return render_template('show_entries.html', entries=entries)



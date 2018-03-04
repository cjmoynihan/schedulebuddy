__author__ = 'cj'
"""
Handles the actual server handling for Flask
"""
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, make_response

from datetime import timedelta
from flask import current_app
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, list):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, list):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

def jsonify(*args, **kwargs):
    from flask import jsonify
    response = jsonify(*args, **kwargs)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

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

app.debug=True

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
            if (request.form['username'],) not in get_db().c.execute("SELECT username FROM users").fetchall():
                error = 'Invalid username'
            elif (request.form['password'],) not in get_db().c.execute("SELECT password FROM users").fetchall():
                error = 'Invalid password'
            else:
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash('You were logged in')
                return redirect(url_for('show_calendar'))
        elif request.form['action'] == 'Add User':
            if (request.form['username'],) in get_db().c.execute("SELECT username FROM users").fetchall():
                error = 'Invalid username'
            else:
                get_db().add_user(request.form['username'], request.form['password'])
                session['logged_in'] = True
                session['username'] = request.form['username']
                flash('User added. You were logged in')
                return redirect(url_for('show_calendar'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/show_calendar')
def show_calendar():
    return render_template('calendar.html')

def write_error(e):
    with open(os.path.join(os.path.dirname(__file__), 'quick_err.txt'), 'a+') as f:
        f.write(str(e) + '\n')


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    try:
        write_error(list(request.args.values()))
        write_error(request.args)
        write_error(request.args['username'])
        get_db().add_event(
            username=request.args['username'],
            event_name=request.args['event_name'],
            start_time=request.args['start_time'],
            end_time=request.args['end_time'],
            days={day: request.args.get(day, False) for day in ('mon','tue','wed','thur','fri','sat','sun')}
        )
    except ValueError as e:
        # raise
        return str(e)
    return "Added event successfully!!"

@app.route('/get_events/<username>')
def get_events(username):
    try:
        return jsonify(get_db().get_sorted_events(username))
    except ValueError as e:
        return str(e)

@app.route('/get_events', methods=['GET', 'POST'])
@crossdomain(origin='*')
def fixed_get_events():
    try:
        return jsonify(get_db().get_sorted_events(request.args['username']))
    except ValueError as e:
        return str(e)

@app.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
    try:
        get_db().add_friend(
            username=request.args['username'],
            friend_username=request.args['friend_username']
        )
        return "Added friend successfully"
    except ValueError as e:
        return str(e)

@app.route('/get_friends/<username>')
def get_friends(username):
    try:
        return jsonify(get_db().get_friends(username))
    except ValueError as e:
        return str(e)


@app.route('/get_friends', methods=['GET','POST'])
@crossdomain(origin='*')
def fixed_get_friends():
    try:
        return jsonify(get_db().get_friends(request.args['username']))
    except ValueError as e:
        return str(e)

@app.route('/get_inverse', methods=['GET', 'POST'])
def get_inverse():
    try:
        return jsonify(
            get_db().get_inverse_schedule(
            friends=request.args['usernames'].split(','),
            start_time=request.args['start_time'],
            end_time=request.args['end_time']
        ))
    except ValueError as e:
        return str(e)


__author__ = 'cj'
"""
Handles the actual server handling for Flask
"""
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

import data_handling as db

app = Flask(__name__)

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


__author__ = 'cj'
import sqlite3 as sq3
import itertools
import bisect
from collections import namedtuple
Event = namedtuple('Event', ['username', 'event_name', 'start_time', 'end_time', 'mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun'])
import os, sys

def write_error(e):
    with open(os.path.join(os.path.dirname(__file__), 'quick_err.txt'), 'a+') as f:
        f.write(str(e) + '\n')

DB_NAME = 'schedule.db'
SCHEMA = 'schema.sql'

DB_NAME, SCHEMA = map(lambda path: os.path.join(os.path.dirname(__file__), path), (DB_NAME, SCHEMA))

class Database:
    def __init__(self):
        self.conn = sq3.connect(DB_NAME)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Creates the tables if they don't already exist
        """
        with open(SCHEMA, 'r') as f:
            for command in ''.join(f.readlines()).split(';'):
                self.c.execute(command)
        self.conn.commit()

    def get_sorted_events(self, username):
        """
        Returns all events for a user, sorted by end_time
        """
        if username not in itertools.chain(*self.c.execute("SELECT username FROM users")):
            raise ValueError("Username {0} doesn't exist".format(username))
        self.c.execute("""
        SELECT event_name, start_time, end_time, mon, tue, wed, thur, fri, sat, sun
        FROM events
        JOIN users ON events.user_id=users.user_id
        JOIN recurring ON events.event_id=recurring.event_id
        WHERE username = ?
        ORDER BY end_time""", (username,))
        return [Event(username, event_name, start_time, end_time, mon, tue, wed, thur, fri, sat, sun)
                for (event_name, start_time, end_time, mon, tue, wed, thur, fri, sat, sun) in self.c]

    def add_user(self, username, password):
        """
        Adds a user to the database
        raises a ValueException if the username already exists in the database
        """
        if username in itertools.chain(*self.c.execute("SELECT username FROM users")):
            raise ValueError("Username {0} is already taken".format(username))
        self.c.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password))
        self.conn.commit()

    def add_event(self, username, event_name, start_time, end_time, **days):
        """
        Adds an event to a users calendar
        raises an exception if the username doesn't exist
        raises an exception if the end_time comes before the start_time
        raises an exception if the start_time is before another event's end_time and after that event's start_time
        raises an exception if the end_time is after another event's start_time and before that event's end_time
        """
        start_time, end_time = map(int, (start_time, end_time))
        # write_error(username)
        if username not in itertools.chain(*self.c.execute("SELECT username FROM users")):
            raise ValueError("Username {0} doesn't exist".format(username))
        if end_time < start_time:
            raise ValueError("Event has start time {0} which is after end time {1}".format(start_time, end_time))
        sorted_events = self.get_sorted_events(username)
        # Get where the new element would fit
        new_event_placement = bisect.bisect_left([int(event.end_time) for event in sorted_events], end_time)
        if new_event_placement > 0 and start_time < sorted_events[new_event_placement-1].end_time:
            raise ValueError("Event {0} starts at {1} before event {2} ends at {3}".format(
                event_name, start_time,
                sorted_events[new_event_placement-1].event_name, sorted_events[new_event_placement-1].end_time))
        if new_event_placement < len(sorted_events) and end_time > sorted_events[new_event_placement].end_time:
            raise ValueError("Event {0} ends at {1} after event {2} starts at {3}".format(
                event_name, end_time,
                sorted_events[new_event_placement].event_name, sorted_events[new_event_placement].start_time
            ))
        self.c.execute("INSERT INTO events(user_id, event_name, start_time, end_time) VALUES(?, ?, ?, ?)",
                       (self.get_id(username), event_name, start_time, end_time))
        self.c.execute("SELECT last_insert_rowid()")
        weekdays = ('mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun')
        self.c.execute("INSERT INTO recurring(event_id, {0}) VALUES(?, ?, ?, ?, ?, ?, ?, ?)".format(', '.join(weekdays)),
                       (self.c.fetchone() + tuple(days.get(weekday, False) for weekday in weekdays)))
        self.conn.commit()

    def get_friends(self, username):
        """
        Returns all the friends' usernames for a specific username
        """
        self.c.execute("""
        SELECT f.username
        FROM friends
        join users u on friends.user_id = u.user_id
        join users f on friends.friend_id = f.user_id
        WHERE u.username = ?
        """, (username,))
        return self.c.fetchall()

    def get_id(self, username):
        """
        Gets the id from a user
        """
        user_id = self.c.execute("SELECT user_id FROM users WHERE username = ?", (username,)).fetchone()
        if user_id is None:
            raise ValueError("User {0} doesn't exist".format(username))
        return int(user_id[0])

    def add_friend(self, username, friend_username):
        """
        Adds a friend to the database as long as it doesn't already exist
        """
        user_id, friend_id = map(self.get_id, (username, friend_username))
        try:
            next(self.c.execute("SELECT * FROM friends WHERE user_id = ? AND friend_id = ?", (user_id, friend_id)))
            raise ValueError("{friend_username} is already a friend of {username}".format(
                friend_username=friend_username, username=username
            ))
        except StopIteration:
            self.c.execute("""
            INSERT INTO friends(user_id, friend_id)
            VALUES(?, ?)
            """, (user_id, friend_id))
            self.conn.commit()

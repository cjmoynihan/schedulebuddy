__author__ = 'cj'
import sqlite3 as sq3
import bisect
from collections import namedtuple
Event = namedtuple('Event', ['username', 'event_name', 'start_time', 'end_time'])

DB_NAME = 'schedule.db'
SCHEMA = 'schema.sql'

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
        if username not in self.c.execute("SELECT username FROM users"):
            raise ValueError("Username {0} doesn't exist".format(username))
        self.c.execute("SELECT event_name, start_time, end_time FROM events WHERE username = ?", (username,))
        return [Event(username, event_name, start_time, end_time)
                for (event_name, start_time, end_time) in
                sorted(self.c.fetchall(), key=lambda event:event[-1])]

    def add_user(self, username, password):
        """
        Adds a user to the database
        raises a ValueException if the username already exists in the database
        """
        if username in self.c.execute("SELECT username FROM users"):
            raise ValueError("Username {0} is already taken".format(username))
        self.c.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password))
        self.conn.commit()

    def add_event(self, username, event_name, start_time, end_time):
        """
        Adds an event to a users calendar
        raises an exception if the username doesn't exist
        raises an exception if the end_time comes before the start_time
        raises an exception if the start_time is before another event's end_time and after that event's start_time
        raises an exception if the end_time is after another event's start_time and before that event's end_time
        """
        if username not in self.c.execute("SELECT username FROM users"):
            raise ValueError("Username {0} is already taken".format(username))
        if end_time < start_time:
            raise ValueError("Event has start time {0} which is after end time {1}".format(start_time, end_time))
        sorted_events = self.get_sorted_events(username)
        # Get where the new element would fit
        new_event_placement = bisect.bisect_left(map(end for (start, end) in sorted_events), end_time)
        if start_time < sorted_events[new_event_placement-1].end_time:
            raise ValueError("Event {0} starts at {1} before event {2} ends at {3}".format(
                event_name, start_time,
                sorted_events[new_event_placement-1].event_name, sorted_events[new_event_placement-1].end_time))
        if end_time > sorted_events[new_event_placement].end_time:
            raise ValueError("Event {0} ends at {1} after event {2} starts at {3}".format(
                event_name, end_time,
                sorted_events[new_event_placement].event_name, sorted_events[new_event_placement].start_time
            ))
        self.c.execute("INSERT INTO events(username, event_name, start_time, end_time) VALUES(?, ?, ?, ?",
                       (username, event_name, start_time, end_time))
        self.conn.commit()

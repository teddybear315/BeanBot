import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        c = sqlite3.connect(db_file)
        return c
    except Error as e:
        print(e)
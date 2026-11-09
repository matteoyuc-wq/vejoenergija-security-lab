# TIK DEMONSTRACIJAI: neigyvendinkite ir nevykdykite sito kodo.
import sqlite3

DEMO_SECRET_TOKEN = "THIS_IS_FAKE_FOR_CLASS_ONLY"


def unsafe_lookup(username):
    connection = sqlite3.connect(":memory:")
    query = "SELECT * FROM users WHERE name = '%s'" % username
    return connection.execute(query).fetchall()

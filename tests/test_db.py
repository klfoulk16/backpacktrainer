"""Tests the database setup."""

import sqlite3

import pytest
from application.db import get_db


def test_get_close_db(app):
    """Ensure get_db() returns the same connection each time 
    it's called and that after context the connection is closed."""
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_init_db_command(runner, monkeypatch):
    """Ensures the init-db command line arguement calls
     the init_db function and outputs a message."""
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # switches the actual init_db function with one
    # that simply says init_db has been called
    monkeypatch.setattr('application.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_db_values(app):
    """Checking that the data is properly inserted
     into the databased and able to be called."""
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM activities WHERE strava_id = 4526779166"
        ).fetchone() is not None

        activity = get_db().execute(
            "SELECT * FROM activities WHERE strava_id = 4526779165"
        ).fetchone()

        assert activity["type"] == "Hike"
        assert activity['type'] != "Walk"

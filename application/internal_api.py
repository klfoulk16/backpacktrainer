"""Internal API calls to database."""

from application.db import get_db


def get_activities():
    """Return all the existing activities.

    :return: List of activities
    :rtype: list
    """
    db = get_db()
    activities = db.execute(
        'SELECT * FROM activities'
    ).fetchall()
    return activities

def insert_activity(activity):
    db = get_db()
    db.execute(
        'INSERT INTO activities (strava_activity_id, type, start_date)'
        ' VALUES (?, ?, ?)',
        (activity['id'], activity['type'], activity['start_date'])
    )
    db.commit()

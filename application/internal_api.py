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

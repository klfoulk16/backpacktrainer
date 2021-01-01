"""Defines app URLS that relate to the training portion of the app."""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from application.db import get_db

bp = Blueprint('trainer', __name__)

# TODO create internal api to get all activities
# TODO test get_activities api
# TODO create strava_api_conn to fetch activities from strava to pop db
# TODO probably don't want to run everytime...create test to make sure new activities were fetched and db populated
@bp.route('/')
def index():
    """Show all the activities."""
    db = get_db()
    activities = db.execute(
        'SELECT * FROM activities'
    ).fetchall()
    return render_template('trainer/index.html', activities=activities)

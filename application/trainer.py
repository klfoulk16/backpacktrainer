"""Defines app URLS that relate to the training portion of the app."""
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from application.internal_api import get_all_activities
from application.strava_api import download_activities

bp = Blueprint('trainer', __name__)

# TODO create test for download activities
# TODO create tests for the previous things - tokens working, responses good,
# getting all activities added after __ time, db insertions working properly
# TODO let's put a nice refresh activities button in upper right hand corner
# so we're not making calls every time we go to index
@bp.route('/')
def index():
    """Show all the activities."""
    download_activities()
    activities = get_all_activities()
    return render_template('trainer/index.html', activities=activities)

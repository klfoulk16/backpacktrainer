"""Testing the process of uploading the CRAW csv's"""
from application.internal_api import insert_activity, parse_description
from application.strava_api import get_last_activity_date
from application.db import get_db

def test_select_last_start_date(app, Activity3):
    # I don't want the app to select a startdate that was manually uploaded
    # it must select a date that came from strava, aka that has a strava activity id
    with app.app_context():
        assert get_last_activity_date() == "2020-12-27T19:45:05Z"
        activity = Activity3
        # activity3 has no id and it's start date is "2021-01-16T14:52:54Z"
        parse_description(activity)
        insert_activity(activity)
        db = get_db()
        assert get_last_activity_date() == "2020-12-27T19:45:05Z"
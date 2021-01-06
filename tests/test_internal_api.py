"""Test our internal api calls."""

import pytest
from application.internal_api import prepare_activities_for_display, get_all_activities, insert_activity, parse_description, get_specific_activity, prepare_detailedactivity_object, meters_to_feet, convert_speed, meters_to_miles
import re
from copy import deepcopy


def test_get_all_activities(app):
    """Test to make sure get_all_activities() returns dict of all activities in
    activities table."""
    with app.app_context():
        activities = get_all_activities()
        assert len(activities) == 2
        assert activities[0]['type'] == 'Hike'
        assert activities[1]['id'] == 4526779166


def test_get_specific_activity(app):
    """Test to make sure we can fetch specific activity based off it's unique strava id."""
    with app.app_context():
        activity_id = 4526779165
        activity = get_specific_activity(activity_id)
        assert activity is not None
        assert activity["id"] == activity_id
        # verify other aspects of what activity 1 should have


def test_prepare_activities_for_display(app):
    """Assert that all activity values are converted to formats easy for reader to understand"""
    with app.app_context():
        a = get_all_activities()
        activities = prepare_activities_for_display(a)
        for activity in activities:
            activity = dict(activity)
            assert type(activity) == dict
            # this isn't perfect because it still matches things like "1:1:12"
            time_format = re.compile(r"^([1-9]?[0-9]:)?([0-9]?[0-9]:)?[0-9][0-9]$")
            # assert speed is changed from seconds per mile to min:sec per mile
            assert time_format.match(activity["average_speed"]) is not None
            assert time_format.match(activity["moving_time"]) is not None
            assert time_format.match(activity["elapsed_time"]) is not None
            # assert Dates are just the day not the time
            date_format = re.compile(r"^[A-Z][a-z]{2}\s[0-9]{2}\s[0-9]{4}")
            assert date_format.match(activity["start_date"]) is not None
            # assert Gear is the name of the gear
            # honestly we could name it anything so can't really check this...

def test_insert_activity(app, Activity1):
    """Ensure activity is properly added to activities table."""
    with app.app_context():
        activity = prepare_detailedactivity_object(Activity1)
        assert activity["type"] in ["Hike", "Walk"]
        # make sure this activity isn't in database already
        assert get_specific_activity(activity["id"]) is None
        insert_activity(activity)
        inserted_activity = get_specific_activity(activity["id"])
        assert inserted_activity is not None
        # verify all important aspects of activity were inserted properly
        assert inserted_activity["id"] == activity["id"]
        assert inserted_activity["distance"] == activity["distance"]
        assert inserted_activity["moving_time"] == activity["moving_time"]
        assert inserted_activity["elapsed_time"] == activity["elapsed_time"]
        assert inserted_activity["total_elevation_gain"] == activity["total_elevation_gain"]
        assert inserted_activity["elev_high"] == activity["elev_high"]
        assert inserted_activity["elev_low"] == activity["elev_low"]
        assert inserted_activity["type"] == activity["type"]
        assert inserted_activity["start_date"] == activity["start_date"]
        assert inserted_activity["average_speed"] == activity["average_speed"]
        assert inserted_activity["gear_id"] == activity["gear_id"]
        assert inserted_activity["weight"] == activity["weight"]
        assert inserted_activity["knee_pain"] == activity["knee_pain"]
        assert inserted_activity["ground_type"] == activity["ground_type"]
        assert inserted_activity["comments"] == activity["comments"]


def test_prepare_detailedactivity_object(Activity1):
    """Assert that activity is properly prepared for db insertion."""
    activity = deepcopy(Activity1)
    assert activity["distance"] != meters_to_miles(Activity1["distance"])
    activity = prepare_detailedactivity_object(activity)
    assert activity["distance"] == meters_to_miles(Activity1["distance"])
    assert activity["total_elevation_gain"] == meters_to_feet(Activity1["total_elevation_gain"])
    assert activity["elev_high"] == meters_to_feet(Activity1["elev_high"])
    assert activity["elev_low"] == meters_to_feet(Activity1["elev_low"])
    assert activity["average_speed"] == convert_speed(Activity1["average_speed"])
    assert activity["weight"] == 10
    assert activity["knee_pain"] == 3
    assert activity["ground_type"] == "trail"
    assert activity["comments"] == "Walked with Jack"


def test_meters_to_feet(Activity1):
    activity = Activity1
    activity["total_elevation_gain"] = meters_to_feet(activity["total_elevation_gain"])
    assert activity["total_elevation_gain"] == 1693.00


def test_parse_description(Activity1, Activity2, Activity3):
    """Assert that function takes an activity, breaks the description down and adds parts to activity dict."""
    activity = parse_description(Activity1)
    assert activity["weight"] == 10
    assert activity["knee_pain"] == 3
    assert activity["ground_type"] == "trail"
    assert activity["comments"] == "Walked with Jack"
    activity = parse_description(deepcopy(Activity2))
    assert activity["weight"] == 0
    assert activity["knee_pain"] == 0
    assert activity["ground_type"] == "snow"
    assert activity["comments"] == "Walked with Jack in Snow"
    activity = parse_description(deepcopy(Activity3))
    assert activity["weight"] == 0
    assert activity["knee_pain"] == 0
    assert activity["ground_type"] == "trail"
    assert activity["comments"] is None

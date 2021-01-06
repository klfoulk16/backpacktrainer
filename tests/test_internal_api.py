"""Test our internal api calls."""

import pytest
from application.internal_api import get_all_activities, insert_activity, parse_description, get_specific_activity, prepare_activity, meters_to_feet, convert_speed, meters_to_miles
from tests.conftest import ActivitySamples
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


def test_insert_activity(app):
    """Ensure activity is properly added to activities table."""
    with app.app_context():
        activity = prepare_activity(deepcopy(ActivitySamples.activity1))
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


def test_prepare_activity():
    """Assert that activity is properly prepared for db insertion."""
    activity = deepcopy(ActivitySamples.activity1)
    assert activity["distance"] != meters_to_miles(ActivitySamples.activity1["distance"])
    activity = prepare_activity(activity)
    assert activity["distance"] == meters_to_miles(ActivitySamples.activity1["distance"])
    assert activity["total_elevation_gain"] == meters_to_feet(ActivitySamples.activity1["total_elevation_gain"])
    assert activity["elev_high"] == meters_to_feet(ActivitySamples.activity1["elev_high"])
    assert activity["elev_low"] == meters_to_feet(ActivitySamples.activity1["elev_low"])
    assert activity["average_speed"] == convert_speed(ActivitySamples.activity1["average_speed"])
    assert activity["weight"] == 10
    assert activity["knee_pain"] == 3
    assert activity["ground_type"] == "trail"
    assert activity["comments"] == "Walked with Jack"


def test_meters_to_feet():
    activity = deepcopy(ActivitySamples.activity1)
    activity["total_elevation_gain"] = meters_to_feet(activity["total_elevation_gain"])
    assert activity["total_elevation_gain"] == 1693.00


def test_parse_description():
    """Assert that function takes an activity, breaks the description down and adds parts to activity dict."""
    activity = parse_description(deepcopy(ActivitySamples.activity1))
    assert activity["weight"] == 10
    assert activity["knee_pain"] == 3
    assert activity["ground_type"] == "trail"
    assert activity["comments"] == "Walked with Jack"
    activity = parse_description(deepcopy(ActivitySamples.activity2))
    assert activity["weight"] == 0
    assert activity["knee_pain"] == 0
    assert activity["ground_type"] == "snow"
    assert activity["comments"] == "Walked with Jack in Snow"
    activity = parse_description(deepcopy(ActivitySamples.activity3))
    assert activity["weight"] == 0
    assert activity["knee_pain"] == 0
    assert activity["ground_type"] == "trail"
    assert activity["comments"] is None

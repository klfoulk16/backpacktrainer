"""Test our internal api calls."""

import pytest
from application.internal_api import (
    get_all_activities,
    insert_activity,
    parse_description,
    get_specific_activity,

    convert_average_speed,
    convert_seconds_h_m_s,
    convert_meters_miles,
    convert_meters_feet,
    convert_date,
    activity_index,
    format_activity_for_view,
    handle_manual_activity_errors
)
from copy import deepcopy


def test_activity_index(app):
    """Test to make sure all activities are fetched from the activities table and properly formated to be displayed in the index."""
    with app.app_context():
        unconverted_activities = get_all_activities()
        converted_activities = activity_index()
        for a in range(len(converted_activities)):
            # assert values were not formttted in unconverted_activities
            assert type(unconverted_activities[a]["moving_time"]) == int
            assert converted_activities[a]["moving_time"] == convert_seconds_h_m_s(unconverted_activities[a]["moving_time"])


def test_format_activity_for_view(app):
    """Assert that function properly prepares an activity from activities table for human viewing"""
    with app.app_context():
        unconverted_activity = get_specific_activity(4526779166)
        converted_activity = format_activity_for_view(unconverted_activity)
        assert type(unconverted_activity["moving_time"]) == int
        assert converted_activity["moving_time"] == convert_seconds_h_m_s(unconverted_activity["moving_time"])
        assert converted_activity["elapsed_time"] == convert_seconds_h_m_s(unconverted_activity["elapsed_time"])
        assert converted_activity["average_speed"] == convert_average_speed(unconverted_activity["average_speed"])
        assert converted_activity["start_date"] == convert_date(unconverted_activity["start_date"])
        assert converted_activity["distance"] == convert_meters_miles(unconverted_activity["distance"])
        assert converted_activity["total_elevation_gain"] == convert_meters_feet(unconverted_activity["total_elevation_gain"])
        assert converted_activity["elev_low"] == convert_meters_feet(unconverted_activity["elev_low"])
        assert converted_activity["elev_high"] == convert_meters_feet(unconverted_activity["elev_high"])


def test_convert_average_speed():
    """Assert converts average speed from meters per second to hours:minutes:seconds per mile."""
    speed = 1
    assert convert_average_speed(speed) == "0:26:49"
    speed = 0
    assert convert_average_speed(speed) == "0:00:00"
    speed = 6.54
    assert convert_average_speed(speed) == "0:04:06"


def test_convert_seconds_h_m_s():
    """Converts time from seconds into H:M:S string."""
    time = 11432
    assert convert_seconds_h_m_s(time) == "3:10:32"


def test_convert_meters_miles():
    """Converts meters to miles i.e. for activity["distance"]"""
    distance = 12345
    assert convert_meters_miles(distance) == 7.67


def test_convert_meters_feet():
    """Converts meters to feet i.e. for activity elevations"""
    distance = 356
    assert convert_meters_feet(distance) == 1168.04


def test_convert_date():
    """Converts date to format Jan 01 2021"""
    date = "2020-12-27T19:45:05Z"
    assert convert_date(date) == "Dec 27 2020"


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


def test_insert_activity(app, Activity1):
    """Ensure activity is properly added to activities table."""
    activity = Activity1
    with app.app_context():
        # make sure this activity isn't in database already
        assert get_specific_activity(activity["id"]) is None
        parse_description(activity)
        handle_manual_activity_errors(activity)
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


def test_parse_description(Activity1, Activity2, Activity3):
    """Assert that function takes an activity, breaks the description down and adds parts to activity dict."""
    parse_description(Activity1)
    assert Activity1["weight"] == 10
    assert Activity1["knee_pain"] == 3
    assert Activity1["ground_type"] == "trail"
    assert Activity1["comments"] == "Walked with Jack"
    parse_description(Activity2)
    assert Activity2["weight"] == 0
    assert Activity2["knee_pain"] == 0
    assert Activity2["ground_type"] == "snow"
    assert Activity2["comments"] == "Walked with Jack in Snow"
    parse_description(Activity3)
    assert Activity3["weight"] == 0
    assert Activity3["knee_pain"] == 0
    assert Activity3["ground_type"] == "trail"
    assert Activity3["comments"] is None


def test_handle_manual_activity_errors(Activity4):
    """Assert handles errors thrown when an activity is missing key:value pairs."""
    handle_manual_activity_errors(Activity4)
    assert Activity4["elev_high"] == 0
    assert Activity4["elev_low"] == 0

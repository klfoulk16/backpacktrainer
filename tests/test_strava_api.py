"""Test our Strava api calls."""

import pytest
import time
from datetime import datetime
from application.strava_api import get_tokens, strava_list_activities_page

# TODO test that initial authentication approval works (and set it up)
# TODO test to make sure get activities returns what's expected
    # make sure get activity only returns new activities or all if none in db
# TODO test to make sure detailed activities returns what's expected

# TODO test that get token request asks for new token if old is expired and that it dumps to file properly and loads from file properly
# TODO test that get activities only asks for new activities (or all if db is empty)

# pytest -v -m webtest to only run functions with webtest
# how do i register this properly in pytest.ini?????
@pytest.mark.skip
def test_get_tokens():
    """Test that strava api call returns token that matches expected format
     and is not expired."""
    tokens = get_tokens()
    assert tokens["token_type"] == "Bearer"
    assert tokens["access_token"] is not None
    assert tokens["expires_at"] is not None
    assert tokens["expires_in"] is not None
    assert tokens["refresh_token"] is not None

    assert "token_type" in tokens
    assert "access_token" in tokens
    assert "expires_at" in tokens
    assert "expires_in" in tokens
    assert "refresh_token" in tokens

    assert tokens["expires_at"] > int(time.time())


# TODO tokens need to be passed in
@pytest.mark.skip
def test_strava_list_activities_page():
    """Test that strava api call returns a 200 reponse and JSON dict of
    activities in expected format."""
    
    # get activities on page that won't have activities
    r = strava_list_activities_page(None, 50)
    assert r.status_code == 200
    assert r.json() is None

    # get values only after certain time
    r = strava_list_activities_page("2020-12-27T19:45:05Z", 1)
    assert r.status_code == 200
    # check that all necessary objects are included
    r_json = r.json()
    assert r_json is not None
    assert "id" in r_json
    assert "type" in r_json
    assert "start_date" in r_json
    # check that we only got objects that occured after last_activity_date param
    for x in r_json:
        assert datetime.strptime(x["start_date"], "%Y-%m-%dT%H:%M:%SZ") < datetime.strptime("2020-12-27T19:45:05Z", "%Y-%m-%dT%H:%M:%SZ")
    
    # check that returns all activities on page
    r_all_none = strava_list_activities_page(None, 1)
    assert r_all_none.status_code == 200
    r_all_none_json = r_all_none.json()
    assert r_all_none_json is not None
    assert "id" in r_all_none_json
    assert "type" in r_all_none_json
    assert "start_date" in r_all_none_json
    # should return all activities because I have none prior to 2020
    r_all_date = strava_list_activities_page("2019-12-22T19:41:05Z", 1)
    assert r_all_date.status_code == 200
    r_all_date_json = r_all_date.json()
    assert r_all_date_json is not None
    assert "id" in r_all_date_json
    assert "type" in r_all_date_json
    assert "start_date" in r_all_date_json

    # test to see if both methods to return all activities on page worked
    assert len(r_all_date_json) == len(r_all_none_json)

    # try to get activities from future is error
    r = strava_list_activities_page("2025-12-22T19:41:05Z", 1)
    assert r.status_code != 200
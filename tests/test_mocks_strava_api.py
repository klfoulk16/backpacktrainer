"""Test our Strava api calls."""

import pytest
import json
from unittest.mock import MagicMock
from application.strava_api import get_tokens, strava_list_activities_page, token_test

# TODO use patches to test that functions work as expected PROVIDED that
# strava works as expected. Aka for now I'll trust that Strava is working as
# expected


def test_token_test(mocker):
    # make sure I'm using mocker right
    mocker.patch("application.strava_api.get_tokens", return_value="token")
    assert token_test() == "token"

# https://www.fugue.co/blog/2016-02-11-python-mocking-101
# https://medium.com/@durgaswaroop/writing-better-tests-in-python-with-pytest-mock-part-2-92b828e1453c
# https://changhsinlee.com/pytest-mock/

@pytest.mark.skip
def test_strava_api_call(mocker):
    # not functional
    mocker.patch(
        "application.strava_api.strava_list_activities_page",
        MagicMock(status_code=200,response=json.dumps({'key':'value'}))
    )
    tokens = {"access_token": "e763t8a194f9e3e2026288778696e54c863c2828"}
    r = strava_list_activities_page("2018-05-02T12:15:09Z", 1, tokens)
    assert r == 200
    assert r.json() == {'key':'value'}


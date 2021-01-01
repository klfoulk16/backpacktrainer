"""Test our internal api calls."""

import pytest
from application.internal_api import get_activities


def test_get_activities(app):
    """Test to make sure get_activities() returns dict of all activities in
    activities table."""
    with app.app_context():
        activities = get_activities()
        assert len(activities) == 2
        assert activities[0]['type'] == 'Hike'
        assert activities[1]['strava_activity_id'] == 4526779166


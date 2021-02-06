# Local imports...
from application.strava_api import get_detailed_activity, get_page_of_activities, download_new_activities

# Third-party imports...
import pytest

# Standard library imports...
from unittest.mock import Mock, patch

# show pass/fail for each test, no long issues
# pytest -v --tb=no

@pytest.mark.skip
def test_get_tokens():
    """I'm not sure how to mock this yet because it writes a file that I don't want overwritten."""
    pass

@pytest.mark.skip
def test_get_initial_token():
    """Eventually I will change this flow so will leave the test till updated."""
    pass

#@pytest.mark.skip
class TestRequestsGet(object):

    @classmethod
    def setup_class(cls):
        cls.mock_get_patcher = patch("application.strava_api.requests.get")
        cls.mock_get = cls.mock_get_patcher.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_get_patcher.stop()

    def test_get_detailed_activity(self, Activity1, StravaTokens1):
        """Assert returns detailed activity object."""
        self.mock_get.return_value = Mock(ok=True)
        self.mock_get.return_value.json.return_value = Activity1
        strava_tokens = StravaTokens1
        response = get_detailed_activity(12345678987654321, strava_tokens)
        assert response.ok is True
        assert response.json() == Activity1

    def test_get_page_of_activities_return_all(self, StravaTokens1, Activity1, Activity2, Activity3):
        """Assert makes correct call if no date is provided."""
        self.mock_get.return_value = Mock(ok=True)
        self.mock_get.return_value.json.return_value = [Activity1, Activity2, Activity3]
        strava_tokens = StravaTokens1
        response = get_page_of_activities(None, 1, strava_tokens)
        assert self.mock_get.called_with("https://www.strava.com/api/v3/activities?access_token="
            + strava_tokens["access_token"]
            + "&per_page=200&page=1")
        assert response.ok is True
        assert response.json() == [Activity1, Activity2, Activity3]

    def test_get_page_of_activities_return_after_date(self, StravaTokens1, Activity1, Activity2, Activity3):
        """Assert makes correct call if date is provided."""
        self.mock_get.return_value = Mock(ok=True)
        self.mock_get.return_value.json.return_value = [Activity1, Activity2, Activity3]
        strava_tokens = StravaTokens1
        response = get_page_of_activities("2018-02-16T14:52:54Z", 1, strava_tokens)
        assert self.mock_get.called_with("https://www.strava.com/api/v3/activities?access_token="
            + strava_tokens["access_token"]
            + "&after=2018-02-16T14:52:54Z&per_page=200&page=1")
        assert response.ok is True
        assert response.json() == [Activity1, Activity2, Activity3]

def test_download_activities(monkeypatch, StravaTokens1, Activity1, Activity2, Activity3):
    """Assert that download activities stops downloading if it recieves an empty list. Also a monkeypatch flex CAUSE I FIGURED IT OUT"""
    class MockResponsePage1:
        status_code = 200
        @staticmethod
        def json():
            return [Activity1, Activity2, Activity3]

    class MockResponsePage2:
        status_code = 200
        @staticmethod
        def json():
            return []
    
    class MockDetailedActivity:
        status_code = 200
        @staticmethod
        def json():
            return Activity1
    
    class Recorder:
        called = 0
    
    def fake_get_tokens():
        return StravaTokens1

    def fake_get_page_of_activities(last_activity_date, page, strava_tokens):
        Recorder.called += 1
        if page == 1:
            return MockResponsePage1()
        else:
            return MockResponsePage2()

    def fake_get_detailed_activity(id, strava_tokens):
        return MockDetailedActivity()
    
    def fake_get_last_activity_date():
        return "Hi I'm not a date"

    def fake_insert_activity(activity):
        pass

    monkeypatch.setattr('application.strava_api.get_page_of_activities', fake_get_page_of_activities)
    monkeypatch.setattr('application.strava_api.get_tokens', fake_get_tokens)
    monkeypatch.setattr('application.strava_api.get_detailed_activity', fake_get_detailed_activity)
    monkeypatch.setattr('application.strava_api.get_last_activity_date', fake_get_last_activity_date)
    monkeypatch.setattr('application.strava_api.insert_activity', fake_insert_activity)

    download_new_activities()

    assert Recorder.called == 2

# Local imports...
from application.strava_api import get_detailed_activity, get_page_of_activities

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

@pytest.mark.skip
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
        self.mock_get.return_value.json.return_value = Activity1
        self.mock_get.return_value = Mock(ok=True)
        self.mock_get.return_value.json.return_value = [Activity1, Activity2, Activity3]
        strava_tokens = StravaTokens1
        response = get_page_of_activities("2018-02-16T14:52:54Z", 1, strava_tokens)
        assert self.mock_get.called_with("https://www.strava.com/api/v3/activities?access_token="
            + strava_tokens["access_token"]
            + "&after=2018-02-16T14:52:54Z&per_page=200&page=1")
        assert response.ok is True
        assert response.json() == [Activity1, Activity2, Activity3]
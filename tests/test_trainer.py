"""Test all routes in the trainer blueprint."""

import pytest


def test_index(client):
    """Make sure no errors when fetching index."""
    assert client.get('/').status_code == 200

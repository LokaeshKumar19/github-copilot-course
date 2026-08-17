"""Pytest configuration and shared fixtures for API tests."""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making requests to the FastAPI app.
    
    Arrange phase: Sets up the client for Act phase in tests.
    """
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of activities for each test.
    
    This fixture ensures test isolation by providing a deep copy of the
    activities dictionary, preventing test interdependence.
    
    Arrange phase: Provides isolated test data.
    """
    return deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities(fresh_activities, monkeypatch):
    """
    Reset the app's activities to fresh state before each test.
    
    Automatically called before each test (autouse=True) to ensure
    the app uses fresh data and tests don't interfere with each other.
    
    Arrange phase: Resets app state before each test.
    """
    # Replace the app's activities with a fresh copy
    monkeypatch.setattr("src.app.activities", fresh_activities)


@pytest.fixture
def sample_activities():
    """
    Provide sample test data with various activity states.
    
    Arrange phase: Provides predefined test data for predictable testing.
    
    Returns:
        dict: Activities with varying participant counts:
              - Chess Club: 2 participants (at capacity? depends on max)
              - Programming Class: 0 participants
              - Gym Class: 1 participant
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@test.edu", "daniel@test.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@test.edu"]
        }
    }

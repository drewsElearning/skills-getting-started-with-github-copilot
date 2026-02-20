import copy
import pytest
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

# Keep an original snapshot of the in-memory store so tests can reset it
initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_db():
    """Restore activities dictionary before each test."""
    activities.clear()
    activities.update(copy.deepcopy(initial_activities))
    yield

client = TestClient(app)


def test_root_redirect():
    # Arrange: nothing special

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    # FastAPI redirect response leads to url attribute
    assert response.url.endswith("/static/index.html")


def test_get_activities():
    # Arrange: ensure there is at least one known activity
    assert "Chess Club" in activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_static_index():
    # Arrange: none

    # Act
    response = client.get("/static/index.html")

    # Assert
    assert response.status_code == 200
    assert "Mergington High School" in response.text


def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    url = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    # Arrange
    existing = activities["Chess Club"]["participants"][0]
    url = f"/activities/{quote("Chess Club")}/signup"

    # Act
    response = client.post(url, params={"email": existing})

    # Assert
    assert response.status_code == 400


def test_signup_not_found():
    # Arrange
    url = f"/activities/{quote("Nonexistent")}/signup"

    # Act
    response = client.post(url, params={"email": "x@x.com"})

    # Assert
    assert response.status_code == 404

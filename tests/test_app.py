from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as api


ACTIVITY_NAME = "Chess Club"
ACTIVITY_PATH = quote(ACTIVITY_NAME, safe="")
EXISTING_EMAIL = "existing@example.com"


@pytest.fixture
def activities(monkeypatch):
    test_activities = {
        ACTIVITY_NAME: {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(api, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities):
    with TestClient(api.app) as test_client:
        yield test_client


def test_get_activities_returns_available_activities(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_PATH}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 409
    assert activities[ACTIVITY_NAME]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    # Arrange
    unknown_activity = "Unknown Club"

    # Act
    response = client.post(
        f"/activities/{quote(unknown_activity, safe='')}/signup",
        params={"email": "new@example.com"},
    )

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[ACTIVITY_NAME]["participants"]


def test_unregister_rejects_unregistered_participant(client, activities):
    # Arrange
    email = "not-registered@example.com"

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_PATH}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert activities[ACTIVITY_NAME]["participants"] == [EXISTING_EMAIL]
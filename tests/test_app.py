from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def restore_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seeded_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["description"] == (
        "Learn strategies and compete in chess tournaments"
    )


def test_new_student_can_sign_up_for_activity(client):
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_for_unknown_activity_returns_not_found(client):
    response = client.post(
        "/activities/Unknown Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_student_cannot_sign_up_twice_for_same_activity(client):
    email = "michael@mergington.edu"
    participants = activities["Chess Club"]["participants"]

    response = client.post(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert participants.count(email) == 1


def test_student_can_unregister_from_activity(client):
    email = "michael@mergington.edu"

    response = client.delete(f"/activities/Chess Club/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_from_unknown_activity_returns_not_found(client):
    response = client.delete(
        "/activities/Unknown Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregistering_non_participant_returns_not_found(client):
    response = client.delete(
        "/activities/Chess Club/signup?email=student@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Student is not signed up for this activity"
    )
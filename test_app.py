from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_new_student_can_sign_up_for_activity():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup?email=" + email)

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_student_cannot_sign_up_twice_for_same_activity():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup?email=" + email)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_student_can_unregister_from_activity():
    email = "michael@mergington.edu"
    response = client.delete("/activities/Chess Club/signup?email=" + email)

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]

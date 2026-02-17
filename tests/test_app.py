from fastapi.testclient import TestClient
import src.app as appmod

client = TestClient(appmod.app)


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should have at least Chess Club entry
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"].get("participants"), list)


def test_signup_and_duplicates():
    activity = "Chess Club"
    # ensure clean state by removing if exists
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    if "test@example.com" in participants:
        client.post(f"/activities/{activity}/unregister?email=test@example.com")

    # sign up new student
    resp = client.post(f"/activities/{activity}/signup?email=test%40example.com")
    assert resp.status_code == 200
    assert "Signed up test@example.com" in resp.json()["message"]

    # duplicate signup should fail
    resp2 = client.post(f"/activities/{activity}/signup?email=test%40example.com")
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Student is already signed up"

    # cleanup
    client.post(f"/activities/{activity}/unregister?email=test%40example.com")


def test_signup_nonexistent():
    resp = client.post("/activities/NoSuchActivity/signup?email=x@x.com")
    assert resp.status_code == 404


def test_unregister_behaviour():
    activity = "Chess Club"
    # make sure student is signed up
    client.post(f"/activities/{activity}/signup?email=remove%40me.com")

    # successful unregister
    resp = client.post(f"/activities/{activity}/unregister?email=remove%40me.com")
    assert resp.status_code == 200

    # unregister again should give 404
    resp2 = client.post(f"/activities/{activity}/unregister?email=remove%40me.com")
    assert resp2.status_code == 404

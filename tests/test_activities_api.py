from src.app import activities


def test_get_activities_returns_seeded_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        payload[expected_activity].keys()
    )


def test_signup_adds_normalized_email(client):
    # Arrange
    activity_name = "Art Studio"
    submitted_email = "  NewStudent@Mergington.edu  "

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": submitted_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Art Studio"
    assert "newstudent@mergington.edu" in activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    missing_activity = "Robotics Lab"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_409_case_insensitive(client):
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "  MICHAEL@mergington.edu "

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Student already registered for this activity"


def test_signup_full_activity_returns_409(client):
    # Arrange
    activity_name = "Debate Team"
    max_participants = activities[activity_name]["max_participants"]
    activities[activity_name]["participants"] = [
        f"student{index}@mergington.edu" for index in range(max_participants)
    ]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "latecomer@mergington.edu"},
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Activity is full"


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Drama Club"
    email = "newactor@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered newactor@mergington.edu from Drama Club"
    assert email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    missing_activity = "Space Club"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_registered_student_returns_404(client):
    # Arrange
    activity_name = "Gym Class"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_matches_email_case_insensitively(client):
    # Arrange
    activity_name = "Basketball Team"
    original_email = "mixedcase@mergington.edu"
    activities[activity_name]["participants"].append(original_email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "  MIXEDCASE@MERGINGTON.EDU  "},
    )

    # Assert
    assert response.status_code == 200
    assert original_email not in activities[activity_name]["participants"]

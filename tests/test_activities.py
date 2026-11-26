import pytest


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected = {
        "Chess Club": {
            "description": "Chess",
            "schedule": "Friday",
            "max_participants": 3,
            "participants": ["first@example.com", "second@example.com"],
        }
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected


def test_signup_adds_participant(client, activity_data):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert activity_data["Chess Club"]["participants"] == [
        "first@example.com",
        "second@example.com",
        email,
    ]


@pytest.mark.parametrize(
    ("activity", "email", "status", "detail"),
    [
        ("Missing", "new@example.com", 404, "Activity not found"),
        (
            "Chess Club",
            "first@example.com",
            400,
            "Student already signed up for this activity",
        ),
    ],
)
def test_signup_errors_leave_participants_unchanged(
    client, activity_data, activity, email, status, detail
):
    # Arrange
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == status
    assert response.json() == {"detail": detail}
    assert activity_data["Chess Club"]["participants"] == original_participants


def test_signup_rejects_full_activity(client, activity_data):
    # Arrange
    participants = activity_data["Chess Club"]["participants"]
    participants.append("third@example.com")
    original_participants = participants.copy()

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": "new@example.com"}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    assert participants == original_participants


def test_signup_requires_email(client, activity_data):
    # Arrange
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.post("/activities/Chess%20Club/signup")

    # Assert
    assert response.status_code == 422
    assert any(error["loc"] == ["query", "email"] for error in response.json()["detail"])
    assert activity_data["Chess Club"]["participants"] == original_participants

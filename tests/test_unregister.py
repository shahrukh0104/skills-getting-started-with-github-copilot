import pytest


def test_unregister_removes_only_the_requested_participant(client, activity_data):
    # Arrange
    email = "first@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert activity_data["Chess Club"]["participants"] == ["second@example.com"]


@pytest.mark.parametrize(
    ("activity", "email", "detail"),
    [
        ("Missing", "first@example.com", "Activity not found"),
        (
            "Chess Club",
            "missing@example.com",
            "Student is not signed up for this activity",
        ),
    ],
)
def test_unregister_errors_leave_participants_unchanged(
    client, activity_data, activity, email, detail
):
    # Arrange
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": detail}
    assert activity_data["Chess Club"]["participants"] == original_participants


def test_unregister_requires_email(client, activity_data):
    # Arrange
    original_participants = activity_data["Chess Club"]["participants"].copy()

    # Act
    response = client.delete("/activities/Chess%20Club/participants")

    # Assert
    assert response.status_code == 422
    assert any(error["loc"] == ["query", "email"] for error in response.json()["detail"])
    assert activity_data["Chess Club"]["participants"] == original_participants

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.activities = patch.dict(
            activities,
            {
                "Chess Club": {
                    "description": "Chess",
                    "schedule": "Friday",
                    "max_participants": 3,
                    "participants": ["first@example.com", "second@example.com"],
                }
            },
            clear=True,
        )
        self.activities.start()
        self.addCleanup(self.activities.stop)
        self.client = TestClient(app)

    def test_removes_only_the_requested_participant(self):
        response = self.client.delete(
            "/activities/Chess%20Club/participants",
            params={"email": "first@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get("/activities").json()["Chess Club"]["participants"],
            ["second@example.com"],
        )

    def test_missing_activity_or_participant_returns_404(self):
        for activity, email in (
            ("Missing", "first@example.com"),
            ("Chess Club", "missing@example.com"),
        ):
            with self.subTest(activity=activity, email=email):
                response = self.client.delete(
                    f"/activities/{activity}/participants", params={"email": email}
                )
                self.assertEqual(response.status_code, 404)
        self.assertEqual(len(activities["Chess Club"]["participants"]), 2)


if __name__ == "__main__":
    unittest.main()

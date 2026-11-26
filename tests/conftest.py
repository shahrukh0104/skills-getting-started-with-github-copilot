import pytest
from fastapi.testclient import TestClient

import src.app as backend


@pytest.fixture
def activity_data(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Chess",
            "schedule": "Friday",
            "max_participants": 3,
            "participants": ["first@example.com", "second@example.com"],
        }
    }
    monkeypatch.setattr(backend, "activities", activities)
    return activities


@pytest.fixture
def client(activity_data):
    with TestClient(backend.app) as client:
        yield client

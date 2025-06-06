import sqlalchemy
from unittest.mock import MagicMock, patch
from src import database as db
import requests
import pytest

db.engine = MagicMock()

from typing import List

BASE_URL = "http://localhost:8000"


def test_create_user():
    resp = requests.post(f"{BASE_URL}/users/create", json={
        "username": "testuser1",
        "password": "testpass1"
    })
    # User may already exist, so accept 201 (created) or 409 (conflict)
    assert resp.status_code in (201, 409)

def test_login_user():
    # Make sure the user exists
    requests.post(f"{BASE_URL}/users/create", json={
        "username": "testuser2",
        "password": "testpass2"
    })
    resp = requests.post(f"{BASE_URL}/users/login", json={
        "Username": "testuser2",
        "password": "testpass2"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_token" in data
    assert data["username"] == "testuser2"
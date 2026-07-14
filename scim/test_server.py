"""
Tests for the minimal SCIM server. Run with: pytest

Covers the lifecycle Okta actually exercises against a SCIM app: auth
rejection, create, filter-based lookup (Okta checks for an existing user
before creating one), PATCH-based deactivation (how Okta actually
deprovisions, not DELETE), and group membership add/remove.
"""

import os

os.environ.setdefault("SCIM_BEARER_TOKEN", "test-token")

from fastapi.testclient import TestClient

from server import app, _USERS, _GROUPS

client = TestClient(app)
AUTH = {"Authorization": "Bearer test-token"}


def setup_function():
    _USERS.clear()
    _GROUPS.clear()


def test_requires_auth():
    response = client.get("/scim/v2/Users")
    assert response.status_code == 401


def test_create_and_get_user():
    response = client.post(
        "/scim/v2/Users",
        json={"userName": "alice@example.com", "name": {"givenName": "Alice"}},
        headers=AUTH,
    )
    assert response.status_code == 201
    user_id = response.json()["id"]

    response = client.get(f"/scim/v2/Users/{user_id}", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["userName"] == "alice@example.com"
    assert response.json()["active"] is True


def test_duplicate_username_rejected():
    client.post("/scim/v2/Users", json={"userName": "bob@example.com"}, headers=AUTH)
    response = client.post(
        "/scim/v2/Users", json={"userName": "bob@example.com"}, headers=AUTH
    )
    assert response.status_code == 409


def test_filter_by_username():
    client.post("/scim/v2/Users", json={"userName": "carol@example.com"}, headers=AUTH)
    client.post("/scim/v2/Users", json={"userName": "dave@example.com"}, headers=AUTH)

    response = client.get(
        '/scim/v2/Users?filter=userName eq "carol@example.com"', headers=AUTH
    )
    assert response.status_code == 200
    body = response.json()
    assert body["totalResults"] == 1
    assert body["Resources"][0]["userName"] == "carol@example.com"


def test_patch_deactivates_user():
    create = client.post(
        "/scim/v2/Users", json={"userName": "erin@example.com"}, headers=AUTH
    )
    user_id = create.json()["id"]

    response = client.patch(
        f"/scim/v2/Users/{user_id}",
        json={"Operations": [{"op": "replace", "path": "active", "value": False}]},
        headers=AUTH,
    )
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_group_membership_add_and_remove():
    user = client.post(
        "/scim/v2/Users", json={"userName": "frank@example.com"}, headers=AUTH
    ).json()
    group = client.post(
        "/scim/v2/Groups", json={"displayName": "Engineering"}, headers=AUTH
    ).json()

    client.patch(
        f"/scim/v2/Groups/{group['id']}",
        json={
            "Operations": [
                {"op": "add", "path": "members", "value": [{"value": user["id"]}]}
            ]
        },
        headers=AUTH,
    )
    response = client.get(f"/scim/v2/Groups/{group['id']}", headers=AUTH)
    assert len(response.json()["members"]) == 1

    client.patch(
        f"/scim/v2/Groups/{group['id']}",
        json={
            "Operations": [
                {"op": "remove", "path": "members", "value": [{"value": user["id"]}]}
            ]
        },
        headers=AUTH,
    )
    response = client.get(f"/scim/v2/Groups/{group['id']}", headers=AUTH)
    assert len(response.json()["members"]) == 0

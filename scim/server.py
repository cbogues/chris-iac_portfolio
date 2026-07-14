"""
Minimal SCIM 2.0 server (RFC 7643 core schema, RFC 7644 protocol) exposing
Users and Groups. Built to be provisioned FROM a real identity provider
(the Okta org from Phase 1 of this repo), not just poked with curl, that's
the point: this gets validated against Okta's actual SCIM provisioning
engine, not a mock of one.

Storage is in-memory on purpose. This is a protocol-depth exercise, not a
production identity store. Swap _USERS / _GROUPS for a real database if you
extend this beyond the portfolio exercise.

Auth: single bearer token, set via SCIM_BEARER_TOKEN. Okta's SCIM app
config supports "HTTP Header" / "OAuth Bearer Token" auth, this matches
that option in the Okta admin console.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Response
import uvicorn

load_dotenv()

app = FastAPI(title="Minimal SCIM 2.0 Server")

BEARER_TOKEN = os.environ.get("SCIM_BEARER_TOKEN", "changeme-dev-token")

# In-memory stores, keyed by the SCIM id we generate (not Okta's internal id).
_USERS: dict[str, dict] = {}
_GROUPS: dict[str, dict] = {}


def _require_auth(authorization: Optional[str]):
    if not authorization or authorization != f"Bearer {BEARER_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _user_resource(user_id: str, body: dict) -> dict:
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
        "id": user_id,
        "userName": body.get("userName"),
        "name": body.get("name", {}),
        "emails": body.get("emails", []),
        "active": body.get("active", True),
        "meta": {
            "resourceType": "User",
            "created": body.get("_created", _now()),
            "lastModified": _now(),
        },
    }


def _group_resource(group_id: str, body: dict) -> dict:
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group_id,
        "displayName": body.get("displayName"),
        "members": body.get("members", []),
        "meta": {
            "resourceType": "Group",
            "created": body.get("_created", _now()),
            "lastModified": _now(),
        },
    }


@app.get("/scim/v2/ServiceProviderConfig")
def service_provider_config():
    """Okta reads this during setup to learn what the server supports."""
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
        "patch": {"supported": True},
        "bulk": {"supported": False},
        "filter": {"supported": True, "maxResults": 200},
        "authenticationSchemes": [
            {"type": "oauthbearertoken", "name": "OAuth Bearer Token", "primary": True}
        ],
    }


# ---------------------------------------------------------------- Users ---

@app.get("/scim/v2/Users")
def list_users(
    authorization: Optional[str] = Header(None),
    filter: Optional[str] = None,
    startIndex: int = 1,
    count: int = 100,
):
    """Okta calls this with filter=userName eq "someone@example.com" before
    creating a user, to check whether it already exists."""
    _require_auth(authorization)
    results = list(_USERS.values())

    if filter and filter.lower().startswith("username eq "):
        target = filter.split(" ", 2)[2].strip('"')
        results = [u for u in results if u.get("userName") == target]

    resources = [_user_resource(u["id"], u) for u in results]

    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "startIndex": startIndex,
        "itemsPerPage": len(resources),
        "Resources": resources,
    }


@app.post("/scim/v2/Users", status_code=201)
def create_user(body: dict, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)

    username = body.get("userName")
    if not username:
        raise HTTPException(status_code=400, detail="userName is required")
    if any(u.get("userName") == username for u in _USERS.values()):
        raise HTTPException(status_code=409, detail="User already exists")

    user_id = str(uuid.uuid4())
    body["id"] = user_id
    body["_created"] = _now()
    _USERS[user_id] = body
    return _user_resource(user_id, body)


@app.get("/scim/v2/Users/{user_id}")
def get_user(user_id: str, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_resource(user_id, user)


@app.put("/scim/v2/Users/{user_id}")
def replace_user(user_id: str, body: dict, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    if user_id not in _USERS:
        raise HTTPException(status_code=404, detail="User not found")
    body["id"] = user_id
    body["_created"] = _USERS[user_id].get("_created", _now())
    _USERS[user_id] = body
    return _user_resource(user_id, body)


@app.patch("/scim/v2/Users/{user_id}")
def patch_user(user_id: str, body: dict, authorization: Optional[str] = Header(None)):
    """Okta deprovisions by PATCHing active=false, not by calling DELETE.
    This is the operation that actually matters for the offboarding story."""
    _require_auth(authorization)
    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for op in body.get("Operations", []):
        path = op.get("path")
        value = op.get("value")
        if path == "active" or (isinstance(value, dict) and "active" in value):
            user["active"] = value if isinstance(value, bool) else value.get("active")

    return _user_resource(user_id, user)


@app.delete("/scim/v2/Users/{user_id}", status_code=204)
def delete_user(user_id: str, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    if user_id not in _USERS:
        raise HTTPException(status_code=404, detail="User not found")
    del _USERS[user_id]
    return Response(status_code=204)


# --------------------------------------------------------------- Groups ---

@app.get("/scim/v2/Groups")
def list_groups(authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    resources = [_group_resource(g["id"], g) for g in _GROUPS.values()]
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "startIndex": 1,
        "itemsPerPage": len(resources),
        "Resources": resources,
    }


@app.post("/scim/v2/Groups", status_code=201)
def create_group(body: dict, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    group_id = str(uuid.uuid4())
    body["id"] = group_id
    body["_created"] = _now()
    _GROUPS[group_id] = body
    return _group_resource(group_id, body)


@app.get("/scim/v2/Groups/{group_id}")
def get_group(group_id: str, authorization: Optional[str] = Header(None)):
    _require_auth(authorization)
    group = _GROUPS.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return _group_resource(group_id, group)


@app.patch("/scim/v2/Groups/{group_id}")
def patch_group(group_id: str, body: dict, authorization: Optional[str] = Header(None)):
    """Handles Okta pushing group membership changes: add/remove members."""
    _require_auth(authorization)
    group = _GROUPS.get(group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    for op in body.get("Operations", []):
        if op.get("path") == "members":
            op_type = op.get("op", "").lower()
            value = op.get("value", [])
            members = group.setdefault("members", [])
            if op_type == "add":
                members.extend(value)
            elif op_type == "remove":
                remove_ids = {v.get("value") for v in value}
                group["members"] = [m for m in members if m.get("value") not in remove_ids]

    return _group_resource(group_id, group)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

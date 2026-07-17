# Phase 4: SCIM 2.0 server

Was stretch goal 3, promoted to a full phase because it genuinely integrates with what's already built instead of standing alone: it gets provisioned FROM the real Okta org from Phase 1, and can optionally be deployed onto the AWS infra from Phase 2.

## Why this exists

Phase 1's Okta work is all admin-console framing: groups, app assignments, managed through Terraform and the UI. That's real, but it doesn't demonstrate protocol-level identity understanding, SCIM, the standard almost every enterprise IdP uses to actually push provisioning events to downstream systems. This phase builds the other side of that conversation: a server that Okta talks to, not a config you push into Okta.

## Prerequisites

- Python 3.10+ (already confirmed working in Phase 3)
- A virtual environment (same pattern as `agent/`)
- Your Phase 1 Okta org, still live
- [ngrok](https://ngrok.com/download) (free tier) for exposing your local server to the internet, Okta's servers call your SCIM endpoint directly, they can't reach `localhost`

## Steps

**Day 1: build and test locally, no Okta involved yet**

```bash
cd scim
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(32))"   # generate a real token
```
Paste the generated token into `.env` in place of the placeholder value.

Run the tests:
```bash
pytest -v
```
All 6 should pass. This proves the SCIM logic (create, filter-lookup, PATCH-based deactivate, group membership) works correctly before any real identity provider touches it.

Start the server locally to sanity-check it by hand:
```bash
python3 server.py
```
In a second terminal:
```bash
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/scim/v2/Users
```
Should return an empty `Resources` list with `totalResults: 0`.

**Day 2: expose it and connect Okta for real**

With the server still running, in a new terminal:
```bash
ngrok http 8000
```
Copy the `https://...ngrok-free.app` URL it gives you.

In your Okta admin console (the same org from Phase 1):
1. **Applications > Browse App Catalog**, search for a SCIM test app that supports bearer token / OAuth bearer auth (Okta publishes one specifically for testing custom SCIM servers, the exact name has shifted over time, search "SCIM" in the catalog and look for one mentioning bearer token or header auth). Add it.
2. In the app's **Provisioning** tab, click **Configure API Integration**, enable it, and set:
   - **SCIM connector base URL**: `https://<your-ngrok-url>/scim/v2`
   - **Unique identifier field**: `userName`
   - **Authentication mode**: HTTP Header / OAuth Bearer Token, paste your token from `.env`
3. Click **Test API Credentials**, it should succeed (this calls `GET /scim/v2/Users` with a filter, which your server already handles).
4. Enable **Create Users**, **Update User Attributes**, and **Deactivate Users** under provisioning settings.
5. Assign a test user (yourself, or a throwaway one) to the app in Okta.

**Day 3: verify the real round-trip**

- Confirm the assigned user shows up via `curl` against your `/scim/v2/Users` endpoint (or check your server's logs/terminal output).
- In Okta, deactivate that user's assignment to the app. Confirm your server receives a PATCH with `active: false`, this is the actual deprovisioning signal, not a DELETE call.
- Create an Okta group, push it to the app, add the test user to it, confirm the group membership PATCH arrives correctly.

**Day 4: write it up**

- Note what actually happened in a short log (timestamps, what Okta sent, what your server did) similar to the evidence sections in the other phases.
- Screenshot: Okta's "Test API Credentials" success message, the provisioning tab showing enabled actions, and your server's terminal output showing incoming requests.

## Expected output

By the end: a passing `pytest` suite, a live `ngrok` tunnel that Okta's "Test API Credentials" accepts, and terminal logs showing at least one real create and one real deactivate request originating from Okta, not from `curl`.

## Rollback

Stop the server (`Ctrl+C`), stop `ngrok` (`Ctrl+C` in its terminal), and in Okta remove the SCIM test app from **Applications** if you don't want it lingering. No persistent state exists beyond the running process, in-memory storage means restarting the server clears everything.

## Edge cases

- **`ngrok` URLs change on every restart** (free tier). If you stop and restart `ngrok`, you have to go back into Okta's provisioning config and update the SCIM connector base URL, or "Test API Credentials" will fail against the old, dead URL.
- **Okta requires HTTPS.** `ngrok` handles this for you (it terminates TLS and forwards to your plain HTTP `localhost:8000`), don't try to point Okta at a bare `http://` URL.
- **In-memory storage means one process only.** If you run the server with multiple workers (`uvicorn --workers 2`), each gets its own empty `_USERS`/`_GROUPS` and they won't agree with each other. Keep it single-process for this exercise.
- **Optional stretch: deploy to AWS instead of `ngrok`.** You could run this on the EC2 instance / public subnet from Phase 2 for a permanent endpoint instead of an ephemeral tunnel, but that requires real TLS termination (a cert via ACM + an ALB, or Caddy/nginx with Let's Encrypt on the instance) and a new security group rule opening the app port to `0.0.0.0/0` (SCIM has to be reachable from Okta's servers, not just your IP, unlike the SSH rule from Phase 2). That's a meaningfully bigger lift than the `ngrok` path, treat it as a follow-on if you want the extra AWS/networking reps, not a requirement to finish this phase.

## Evidence

Verification pass from 2026-07-16, against the real Okta org from Phase 1 via an `ngrok` tunnel. Screenshots in `../docs/screenshots/` where noted; the request log below is pulled directly from the running server's terminal output since it's more useful as text than as an image.

**Okta credentials verified**
![SCIM 2.0 Test App verified successfully](../docs/screenshots/Screenshot%202026-07-16%20at%207.24.28%20PM.png)
"Test API Credentials" succeeding, confirming Okta could authenticate against the live `ngrok`-tunneled server.

**Group pushed and active**
![Push Groups showing IT-Admins active](../docs/screenshots/Screenshot%202026-07-16%20at%207.25.27%20PM.png)
`IT-Admins` (the same group from Phase 1's Okta module) pushed to the SCIM app, status "Active", last push timestamped.

### Troubleshooting notes (kept, not cleaned up, same policy as Phase 1's CI evidence)

- **"Provided Base URL does not match required pattern"**: hit this first, on a syntactically valid `https://` URL. Turned out to be a stale inline validation message from the form field, resolved by retyping the value cleanly.
- **"Invalid or missing bearer token" despite pasting the token correctly**: the Okta field expects the raw token only. Okta constructs the full `Authorization: Bearer <value>` header itself, if you type `Bearer <token>` into the field, the real request becomes `Authorization: Bearer Bearer <token>`, which the server correctly rejects. Confirmed by inspecting the actual outbound request in the `ngrok` local inspector at `127.0.0.1:4040`, that's what caught it, guessing from the error message alone wasn't enough.

### Real request log (chronological, from the server's terminal)

```
GET   /scim/v2/Groups                                                    200 OK
GET   /scim/v2/Users?filter=userName eq "chris.bogues@protonmail.com"    200 OK
POST  /scim/v2/Users                                                     201 Created
PATCH /scim/v2/Users/7a328083-07f4-439f-bcef-77d2c6da7f51                200 OK   # deactivation (unassigned from app)
POST  /scim/v2/Groups                                                    201 Created
GET   /scim/v2/Groups                                                    200 OK
PATCH /scim/v2/Users/7a328083-07f4-439f-bcef-77d2c6da7f51                200 OK   # reactivation (reassigned to app)
GET   /scim/v2/Users                                                     200 OK
GET   /scim/v2/Users/7a328083-07f4-439f-bcef-77d2c6da7f51                200 OK
PUT   /scim/v2/Users/7a328083-07f4-439f-bcef-77d2c6da7f51                200 OK
GET   /scim/v2/Groups/82e28978-3a07-44a0-aaba-fc6c242c13da               200 OK
PATCH /scim/v2/Groups/82e28978-3a07-44a0-aaba-fc6c242c13da               200 OK   # membership sync
PATCH /scim/v2/Groups/82e28978-3a07-44a0-aaba-fc6c242c13da               200 OK   # membership sync
```

Every request originated from Okta's real infrastructure (source IPs `44.238.82.114` and `35.81.223.96`, visible in the `ngrok` inspector), not from `curl` or a test script.

### Server-side confirmation of the deactivation

```
$ curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/scim/v2/Users/7a328083-07f4-439f-bcef-77d2c6da7f51
{"schemas":["urn:ietf:params:scim:schemas:core:2.0:User"],"id":"7a328083-07f4-439f-bcef-77d2c6da7f51","userName":"chris.bogues@protonmail.com","name":{"givenName":"Chris","familyName":"Bogues"},"emails":[{"primary":true,"value":"chris.bogues@protonmail.com","type":"work"}],"active":false,"meta":{"resourceType":"User","created":"2026-07-17T04:27:31Z","lastModified":"2026-07-17T04:30:48Z"}}
```

`active: false`, confirming the PATCH from Okta actually took effect, not just that a 200 was returned.

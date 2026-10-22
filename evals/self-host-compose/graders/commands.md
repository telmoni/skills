---
type: llm
---

PASS if the reply gives `docker compose -f deploy/compose/docker-compose.yml up -d`, run from inside the clone, tells the user to back up `TELEMETRY_KEK` and `CONNECTOR_KEK` alongside the database dumps, and calls `ADMIN_EMAIL` and `ADMIN_PASSWORD` bootstrap-only, with an OIDC provider and `AUTH_DISABLE_USERNAME_PASSWORD=true` for production.
FAIL if any of these is missing.

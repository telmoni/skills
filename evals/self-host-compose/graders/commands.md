---
type: llm
---

PASS if the reply gives `docker compose -f deploy/compose/docker-compose.yml up -d`, run from inside the clone, tells the user to back up `CONNECTOR_KEK` alongside the database dumps, and calls `ADMIN_EMAIL` and `ADMIN_PASSWORD` bootstrap-only, with an OIDC provider and `DISABLE_LOGIN_FORM=true` for production.
FAIL if any of these is missing.

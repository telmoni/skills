---
type: llm
focus:
  source: file
  path: telmoni/deploy/compose/.env
---

PASS if the file sets `SERVICE_SECRET`, `AUTH_SECRET` and `POSTGRES_PASSWORD` to 64-character hexadecimal values, sets `CONNECTOR_KEK` to `local:` followed by 64 hexadecimal characters, and carries none of the development template's keys, such as `AUTH_DATABASE_URL`, `MIGRATOR_DATABASE_URL` or an `SMTP_URL` pointing at Mailpit.
FAIL if any secret is missing, short, or a placeholder, or if keys from the development template appear.

---
type: llm
focus:
  source: file
  path: src/app.js
---

PASS if POST /webhooks/telmoni is registered before the app-wide `express.json()`, or is otherwise kept out of it, so that its handler can read the raw request bytes; the raw-body parser itself may live in `src/telmoni-webhook.js`.
FAIL if the app-wide `express.json()` still runs before the webhook route, or if nothing in this file mounts the webhook route.

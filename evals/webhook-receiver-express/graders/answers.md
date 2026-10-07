---
type: llm
focus:
  source: file
  path: src/telmoni-webhook.js
---

PASS if all of these hold: a verified delivery whose `kind` is not `member_added` is answered with a 2xx; the route never answers 410; and the code itself recognises a repeated delivery by its `Telmoni-Delivery-Id` header or the body's `id`, and does not hand it to `onMemberAdded` a second time.
FAIL if unhandled kinds get a 4xx or 5xx, if any path answers 410, or if repeats are left to `onMemberAdded` (or to the user) to handle.

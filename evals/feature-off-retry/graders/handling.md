---
type: llm
focus:
  source: file
  path: sync.py
---

PASS if all of these hold: the script reads the problem document and decides by its `type`, so a 503 of another type (such as `/errors/agent/disabled`, or a body that is not a problem document) is not retried as if it were feature-off; on `/errors/tenant/feature-off` and `/errors/tenant/rate-limited` it waits at least `Retry-After` (or `retry_after_secs`) before trying again, with a bound on attempts or total wait; a `401` `/errors/auth/invalid-token` stops the run without retrying; a run that gives up exits non-zero before the CRM step; and the API key is still read from `TELMONI_API_KEY` and never printed.
FAIL if any one of these fails, including a script that retries every 503 whatever its `type`.

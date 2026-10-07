---
type: llm
focus:
  source: file
  path: src/telmoni-webhook.js
---

PASS if the verification does all of the following: splits the `Telmoni-Signature` header into `t` and every `v1`; refuses a delivery whose `t` is more than 300 seconds from the current time; computes HMAC-SHA256 keyed with the whole secret, `whsec_` prefix included, over `{t}.` followed by the raw request bytes; and accepts the delivery when any `v1` matches, compared in constant time.
FAIL if any one of these is missing or wrong: for example the prefix is stripped or the secret decoded, the HMAC covers a re-serialised JSON body, the comparison uses `===`, or only the first `v1` is checked.

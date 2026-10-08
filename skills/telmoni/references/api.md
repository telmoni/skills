---
description: Call Telmoni's read-only `/v1` API with a project API key, handle its problem-document errors and rate limits, rotate a key without downtime, or use the configuration-only SDKs.
---

# The /v1 API and API keys

Fetch the page before writing a client: https://telmoni.com/docs/api/reference (routes and fields), https://telmoni.com/docs/api/api-keys (minting, rotation, revocation), https://telmoni.com/docs/errors (every error type).

## What exists

- Two routes, `GET /v1/organization` and `GET /v1/members`, under the deployment's origin: `${TELMONI_ENDPOINT:-https://telmoni.com}/v1`. They take `GET` and `HEAD`, nothing writes, and nothing paginates: `/v1/members` returns the whole roster.
- A key is minted in one project, by its Owner or an Admin, on the console's `/{organization}/{project}/api-keys` page. It reads that project's organization and that project's roster, never the whole organization's roster. The key alone decides the scope: an organization or project header is dropped.
- The SDKs (TypeScript, Python, Go, Rust) hold an endpoint, a key and an organization ID, and send no requests. None is published to a registry, so install from the repository as `api/sdks` shows: a `telmoni` package on npm, PyPI or crates.io is not Telmoni's. For a client today, write plain HTTP calls to the two routes, and never call an SDK method that `sdk/` in `telmoni/telmoni-cli` doesn't define.

## Calling it

- Send `Authorization: Bearer $TELMONI_API_KEY`, with the key read from the environment or a secret store. Keys are server-side only: never in browser, mobile or other client-side code.
- Check a key with `curl -sS -H "Authorization: Bearer $TELMONI_API_KEY" "${TELMONI_ENDPOINT:-https://telmoni.com}/v1/organization"`.
- Store `organization_id`, never `slug`: a slug moves when the organization's URL changes.

## Errors

Every error is an RFC 9457 problem document (`application/problem+json`). Branch on `type`, which is the same on every deployment; `detail` is for people and may be absent.

| Answer | What the client does |
|---|---|
| `401` `/errors/auth/invalid-token` | The key is revoked, expired or unknown, or its organization is being deleted. Stop; the user mints or rotates a key in the console. |
| `429` `/errors/tenant/rate-limited` | Wait for `Retry-After`. The limits are 600 requests a minute per key and 1,200 per source address. |
| `503` `/errors/tenant/feature-off` | The API is switched off for the organization or the deployment; the route still exists, and the `flag` field names the switch. Wait for `Retry-After` and retry; tell the user if it persists. |
| `503` `/errors/upstream-unavailable` or `/errors/auth/identity-unavailable` | Retry with backoff. On a self-hosted deployment, the first persisting can mean the console's `SERVICE_SECRET` no longer matches the server's; the second, that the server cannot reach its database. |
| `404` `/errors/auth/not-found` | No such route under `/v1`. |

## Rotating a key

Rotate rather than revoke a key in use. **Rotate** on the key's row returns a new token, shown once, and the old token keeps working for 24 hours or until its own expiry, whichever comes first: deploy the new one inside that window. The replacement expires 90 days after rotation, whatever the old key's term. **Revoke** ends a key at once, for one that leaked.

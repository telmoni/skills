---
description: Call Telmoni's read-only `/v1` API with a project API key, send spans to `/otlp/v1/traces` with an SDK or an exporter, handle the problem-document errors and rate limits, or rotate a key without downtime.
---

# The /v1 API, ingest and API keys

Fetch the page before writing a client: https://telmoni.com/docs/api/reference (routes and fields), https://telmoni.com/docs/api/ingest (sending spans), https://telmoni.com/docs/api/field-inventory (every attribute ingest reads, and what becomes of each), https://telmoni.com/docs/api/api-keys (minting, scopes, rotation, revocation), https://telmoni.com/docs/errors (every error type).

## What exists

- Two routes, `GET /v1/organization` and `GET /v1/members`, on the machine host: `${TELMONI_ENDPOINT:-https://api.telmoni.com}/v1` (a self-hosted deployment's own machine host, or its console's host where the lanes are routed by path). They take `GET` and `HEAD`, nothing writes, and nothing paginates: `/v1/members` returns the whole roster.
- A key is minted in one project, by its Owner or an Admin, on the console's `/{organization}/{project}/api-keys` page, with one or both scopes: `read` opens `/v1`, `ingest` opens `/otlp/v1/traces`; a live key without the scope a lane needs gets `403` `/errors/authz/forbidden`. It reads that project's organization and that project's roster, never the whole organization's roster. The key alone decides the project: no header picks another.
- The SDKs (Python, TypeScript, Go, Rust) record an agent's runs, and the steps, model calls and tool calls inside each, as OpenTelemetry spans sent to `/otlp/v1/traces` with a key holding the `ingest` scope (`TELMONI_API_KEY`); they call nothing else, so a read of `/v1` is still a plain HTTP call. Each runs a tracer provider of its own beside the application's OpenTelemetry, reading none of its `OTEL_*` variables, sends nothing outside a run, and takes content off every span before it leaves: `capture_content` sends it only to a project whose content mode is `on`, and every project is `off` today, so no setting records prompts, completions or tool payloads. None is on a package registry yet: install from the repository as `api/sdks` shows, and treat a `telmoni` package on npm, PyPI or crates.io as not Telmoni's. Use only the methods `api/sdks` documents.

## Calling it

- Send `Authorization: Bearer $TELMONI_API_KEY`, with the key read from the environment or a secret store. Keys are server-side only: never in browser, mobile or other client-side code.
- Check a key holding `read` with `curl -sS -H "Authorization: Bearer $TELMONI_API_KEY" "${TELMONI_ENDPOINT:-https://api.telmoni.com}/v1/organization"`. A key holding only `ingest`, as one in an agent's process should, gets `403` there while it works: test it against `/otlp/v1/traces`, where `401` is a dead key and `403` one without the scope.
- Store `organization_id`, never `slug`: a slug moves when the organization's URL changes.

## Sending spans

- `POST ${TELMONI_ENDPOINT:-https://api.telmoni.com}/otlp/v1/traces` takes OTLP/HTTP — `Content-Type: application/json` (OTLP's JSON) or `application/x-protobuf`, gzip allowed — with a key holding the `ingest` scope. One to 1,000 spans and at most 1 MiB decompressed per export; 600 exports a minute per project.
- A span is kept only with `telmoni.run_id` (a UUID, the same on every span of one run) and `telmoni.agent` on it; every other span is refused one by one and named in the answer's `partialSuccess`. The SDKs set both on every span inside a run; a stock OpenTelemetry exporter sets neither and sends nothing that is kept. Say so before pointing an exporter at it.
- Prompts, completions, tool payloads and the `user.*` attributes that name a person (`user.name`, `user.email`, `user.full_name`) are dropped at the door on an `off` project, which every project is today, and named in the answer; `user.id`, the end user's own id, is the one `user.*` attribute kept, stored hashed under the project's key. The field inventory (`api/field-inventory`) is the whole list of what ingest reads — the attribute, the spans it is read on, the column or map it is kept in or the drop, the content mode it needs, and its rule — held to the server's code by a test, and shown as the same list on a project's **Privacy** page in the console beside the project's content mode. Answer "is X kept?" from that page, never from memory: text it does not name is dropped in every mode as `unlisted`, and a number or boolean it does not name is kept on a span and dropped on the resource.
- A refusal on this lane is OTLP's `Status` (`{"code", "message"}`) in the request's encoding, never a problem document; the message opens with the error type. An export sent again within an hour with the same bytes gets its first answer again and is not written twice; `429` and `503` are the two to retry, after `Retry-After` where the answer gives one.

## Errors

Every error on `/v1` is an RFC 9457 problem document (`application/problem+json`). Branch on `type`, which is the same on every deployment; `detail` is for people and may be absent.

| Answer | What the client does |
|---|---|
| `401` `/errors/auth/invalid-token` | The key is revoked, expired or unknown, or its organization is being deleted. Stop; the user mints or rotates a key in the console. |
| `429` `/errors/tenant/rate-limited` | Wait for `Retry-After`. The limits are 600 requests a minute per key and 1,200 per source address. |
| `503` `/errors/tenant/feature-off` | The API is switched off for the organization or the deployment; the route still exists, and the `flag` field names the switch. Wait for `Retry-After` and retry; tell the user if it persists. |
| `503` `/errors/auth/identity-unavailable` | Retry with backoff: the server could not read its database while checking the key. One that persists on a self-hosted deployment means the server cannot reach Postgres. |
| `404` `/errors/not-found` | No such route under `/v1`. `/errors/auth/not-found` is a different answer: a lane that looked for something and did not find it. |

## Rotating a key

Rotate rather than revoke a key in use. **Rotate** on the key's row returns a new token, shown once, and the old token keeps working for 24 hours or until its own expiry, whichever comes first: deploy the new one inside that window. The replacement expires 90 days after rotation, whatever the old key's term. **Revoke** ends a key at once, for one that leaked.

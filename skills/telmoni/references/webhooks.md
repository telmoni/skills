---
description: Build, test or debug an endpoint that receives Telmoni's signed webhook deliveries — verifying `Telmoni-Signature`, answering, deduplicating, testing locally, rotating the secret.
---

# Receiving Telmoni webhooks

Fetch https://telmoni.com/docs/integrations/webhooks before writing code, and port its verifier (Node and Python are on the page) into the user's stack: the page is kept in step with the platform's signer. What follows is where receivers go wrong.

## Verify over the exact bytes

- The signature covers `{t}.{body}`, where `body` is the raw request bytes. Read them before anything parses JSON, because a parsed and re-serialised body does not match: in Express, mount `express.raw({ type: "application/json" })` on this route instead of `express.json()`; in a Next.js route handler, `await request.text()` (a Pages Router API route also needs `bodyParser: false`); in FastAPI, `await request.body()`; in Flask, `request.get_data()`; in Django, `request.body`.
- The HMAC key is the whole secret, `whsec_` included. Don't strip the prefix or base64-decode the rest the way Svix verifiers do; the scheme is Stripe's.
- `Telmoni-Signature` carries one `v1` per live secret, two while a rotation overlaps. Accept the delivery if any `v1` matches, compared in constant time.
- Refuse a `t` more than 300 seconds from the receiver's clock. Every attempt is re-signed when sent, so a retry after a long backoff still carries a fresh `t`.
- Keep the secret in the environment or a secret store (for example `TELMONI_WEBHOOK_SECRET`). The console shows it once, when the webhook is connected or its secret rotated, so the user copies it there; never ask for it in the conversation or print it.
- The body names no project or organization, and each project's webhook has its own secret. A receiver serving several projects gives each its own URL (a path segment is enough) and picks the secret by URL.

## Answer

- Return a 2xx as soon as the event is stored and do the work afterwards: the request has a ten-second budget, and anything but a 2xx is retried, by default five attempts over about 45 minutes.
- Redirects are not followed, so a `3xx` (an HTTPS or trailing-slash redirect) is a failed send: connect the final URL.
- Deduplicate on `Telmoni-Delivery-Id`, which equals the body's `id` and repeats across retries and manual resends.
- Answer a `kind` the receiver doesn't handle with a 2xx. **All events** includes kinds added later, an error turns each into five failed attempts, and ten failed sends in a row mark the webhook **Needs attention**.
- Return `410` only for an endpoint that is gone for good. One `410` marks the webhook **Needs attention** at once and fails its queue, and nothing raised until someone rotates its secret is ever delivered. During a deploy or a move, answer `404` or `503` and let the retries carry it.

## Test

1. Unit-test the verifier with the test vector on the webhooks page (secret, header, body and `t`), copied from the page rather than from memory, with the body as that exact string rather than an object you serialise: it must accept the triple with the clock fixed at that `t`, and refuse it with one byte of the body changed.
2. End to end: connecting refuses `http://`, loopback, private and link-local addresses and names such as `localhost` or `*.internal`, with no development override. Expose the local receiver through a public HTTPS tunnel (for example `cloudflared tunnel --url http://localhost:<port>`), connect that URL on the project's **Connectors** page (`/{organization}/{project}/connectors`), and select **Send test**, which posts one signed `connector_connected` body.
3. A quick tunnel's URL changes on every run, and a project connects a URL once (a second time is `409`): disconnect the old row and connect the new URL.

The Connectors page keeps each delivery's attempts, statuses and timing for 30 days, and **Resend** replays a delivery with its original `Telmoni-Delivery-Id`.

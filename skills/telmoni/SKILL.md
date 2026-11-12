---
name: telmoni
description: Connects applications and coding-agent sessions to Telmoni, open-source monitoring for AI agents. Adds tracing of agent executions, model calls, tool calls and retrievals with the Telmoni SDKs (Python, TypeScript/JavaScript, Go, Rust) or an existing OpenTelemetry GenAI instrumentation, and installs and troubleshoots the Telmoni observability plugins for Claude Code, Codex and Antigravity. Use when the user mentions Telmoni, asks to trace, monitor or observe an AI agent or LLM application, to send OTLP traces to Telmoni, to record their coding agent's sessions, or asks why traces are not showing up in Telmoni.
---

# Telmoni

Telmoni records what an AI agent did as traces: each execution, its model calls and their tokens, its tool calls and retrievals. This skill connects one of two things to it. Decide which first.

| The user wants to monitor | Do this |
|---|---|
| Their coding agent's own sessions (Claude Code, Codex, Antigravity) | Follow [Coding-agent plugins](references/plugins.md). No application code changes. |
| An application they are building | Follow the workflow below. |

If "monitor my agent" could mean either, ask which. Installing this skill installs no plugin and no SDK by itself.

## Workflow for an application

1. **Inspect** the language, dependency versions, where an agent execution starts and ends, the provider calls, streaming, existing telemetry, and how the process shuts down. Follow the repository's own instructions and its rules for adding dependencies.
2. **Choose one route** per operation, so no model or tool call is recorded twice:
   - Explicit instrumentation in Python, TypeScript/JavaScript, Go or Rust: read [SDK integration](references/sdks.md). This is the default.
   - A framework that already emits OpenTelemetry GenAI spans, or a request for native OTLP: read [Framework and OTLP integration](references/otlp.md).
3. **Configure** the endpoint and key (below).
4. **Install the SDK and read the version you got.** The examples in [SDK integration](references/sdks.md) use the current source's names. The first published version, 0.2.0, names things differently and lacks some options: if that is what installed, use its [Versions](references/sdks.md#versions) table instead of copying an example. Then read the installed package's own signatures before writing any call: Python docstrings, the TypeScript `.d.ts` files, `go doc`, or the crate source under the Cargo registry. A published package carries no README.
5. **Instrument** (below), preserving behavior: return values, raised errors, streaming and existing telemetry stay as they were.
6. **Verify** (below), then **report**.

For API details beyond the references, read the SDK's README and source or the docs in [telmoni/telmoni](https://github.com/telmoni/telmoni) (`sdk/<language>/`, `web/content/docs/`). Do not assume a checkout exists at a fixed path on the user's machine.

## Configure

| Variable | Value |
|---|---|
| `TELMONI_API_KEY` | A project API key with the `ingest` scope (**Send spans**), created by the user on the project's **API keys** page |
| `TELMONI_ENDPOINT` | The deployment's machine endpoint, as a base URL such as `http://localhost:8082` |
| `TELMONI_ENVIRONMENT`, `TELMONI_RELEASE` | Optional: where it runs and which version |
| `TELMONI_ORG` | Only where the deployment needs an organization identifier |

- The endpoint is never the console's URL and never ends in `/otlp/v1/traces`; the SDK adds the path. SDKs require HTTPS except for loopback hosts, and refuse redirects.
- The key lives in the server-side environment. Never ask for it in chat, print it, log it, or put it in committed code or a client or browser bundle. Add placeholder names to an existing environment example file where the repository has one.
- The SDKs do not read `OTEL_*` variables; a native OTLP exporter uses its own configuration ([OTLP](references/otlp.md)).
- Ask the user for a missing endpoint or project while continuing with the changes that do not depend on it.

## Instrument

- **One client per process**, created once and reused.
- **One root trace per agent execution**: one request, job or turn. Not one per process, and not one per conversation. Give it a stable agent name, and attach the application's own session and user ids so Telmoni can group traces. An internal id such as a customer number is right: the user id is hashed at ingest. Never an email address, a name or any other personal text.
- **Wrap the real operations inside the root**: each model call, tool call and retrieval, with steps for meaningful stages. Use stable operation names.
- **Record what the provider reported**: the requested model and provider, then the response model and token usage from the response. Leave usage unset where the provider gives none; never estimate it.
- **Name the prompt** where the application has named, versioned prompts and the installed SDK has the option (the current source does; 0.2.0 does not): the model call's prompt name and version are metadata Telmoni compares versions by.
- **A session id** only where the application already has one; leave it unset otherwise. Never invent one.
- **Write the content calls once.** Passing messages or tool results, and calling `returned` and `answered`'s message fields, is safe with capture off: the SDK drops the content and keeps the counts. Do not leave them out to keep content private, and do not branch on the capture setting.
- **Streaming**: keep the model call open until the stream is consumed, failed or cancelled, and record usage when the provider delivers it.
- **Errors**: preserve results and re-raise failures. Python context managers and TypeScript callbacks record an escaping error; Go and Rust handles need the failure marked explicitly. Treat cancellation separately where the application exposes it.
- **Lifetime**: end children before the root, and the root before flushing. Flush after short-lived work; shut down once at process teardown, never after each request on a shared client.
- **The application's own OpenTelemetry**: the SDK owns a tracer provider beside the application's. Do not replace the global provider, and do not expect existing application spans to be exported by the SDK. Across services, use the SDK's inject and extract.

## Keep content private

Leave content capture off unless the user asks for it. It is off by default in every SDK: the config field `capture_content` (Python, Rust), `captureContent` (TypeScript) or `CaptureContent` (Go), and in current SDKs `TELMONI_CAPTURE_CONTENT=1` from the environment. Never set it unasked. Content (messages, tool payloads, retrieved text, exception messages and stacks) leaves the process only when that switch is on **and** the project's content mode is `on`; turning it on locally is not enough.

Metadata always travels: span names, tags, identifiers, scores and custom attributes are not covered by the content mask. Keep prompts, secrets, emails and other personal text out of them, and use opaque identifiers. Current SDKs also scrub secrets from content by default (`TELMONI_SCRUB_SECRETS=0` turns it off, `TELMONI_SCRUB_PII=1` turns personal-data scrubbing on): leave it as it is. It does not make arbitrary metadata safe, and SDK 0.2.0 has no scrubber at all.

A third-party instrumentation may send content by default even where Telmoni drops it at ingest. Check its own client-side content setting; the project's content mode does not stop transmission.

## Verify

1. Run the repository's own checks for the code changed.
2. Exercise one execution with a mocked provider or an existing cheap development path, with synthetic input and capture off. Do not make paid model calls or send customer content to demonstrate tracing.
3. Read the SDK's warnings: it reports a refused batch, a rejected key or a bad endpoint once each. Python writes them to the `telmoni` logger, TypeScript to `console.warn`, Go to `slog` (or the `*slog.Logger` given to `WithLogger`), and Rust through `tracing::warn!` under the target `telmoni`, which shows only where the application has a subscriber. Fix what they name before adding retries or changing providers.
4. Confirm the trace arrived. `flush` returns `False` or `false` in Python, TypeScript and Rust, and an `error` in Go, when a batch could not be sent: check it. A flush that succeeds still does not show what the server kept. Either the user checks the project's **Traces** page for the root, its nested calls, the model's usage and the error behavior, or, where the configured key also holds the `read` scope, read it back without printing the key:

   ```sh
   curl -fsS -H "Authorization: Bearer $TELMONI_API_KEY" \
     "$TELMONI_ENDPOINT/v1/traces?agent=<agent-name>&days=1&limit=1"
   ```

   A `403` means the key has no `read` scope: ask the user to look instead.

## Report

State the files changed, the checks run, the configuration the user still has to supply, and whether a trace was actually seen in Telmoni. Without credentials or a deployment, finish the code and say that delivery end to end is unverified.

## Availability

Telmoni is self-hosted only: there is no hosted service and no public docs site. Always set the deployment's endpoint explicitly (the SDKs, CLI and plugins have no default), and use the source docs in the repository (`web/content/docs` in `telmoni/telmoni`). If a package is missing from its registry, report that as a blocker; do not invent a package name or silently install from an unreleased checkout.

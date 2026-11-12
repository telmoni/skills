# Framework and OTLP integration

Use this route when the application already uses compatible instrumentation or the user requests a native OpenTelemetry integration. Consult Telmoni's maintained [framework guide](https://github.com/telmoni/telmoni/blob/main/web/content/docs/api/frameworks.mdx) for the detected framework/version and its content settings before adding packages. It has a section each for the OpenAI SDK, the Anthropic SDK, LangChain and LangGraph, the OpenAI Agents SDK, CrewAI, LiteLLM and the Vercel AI SDK; for anything else, use the [SDK route](sdks.md) or check its spans against the ingest contract below. Do not install every framework's instrumentation.

## Export

Telmoni accepts OTLP over HTTP at the deployment's machine endpoint plus `/otlp/v1/traces`, authenticated with `Authorization: Bearer <ingest-api-key>`. A native OTLP exporter typically uses:

```sh
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://YOUR_TELMONI_HOST/otlp/v1/traces
export OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer%20YOUR_INGEST_API_KEY"
export OTEL_SERVICE_NAME=support-bot
```

These are placeholders, not working credentials. The environment header syntax URL-encodes the space as `%20`; direct HTTP headers use a literal space. Ingest takes OTLP's JSON or protobuf encoding over HTTP, gzipped or not, and no gRPC: set an exporter that defaults to gRPC to HTTP/protobuf using its supported options. Do not point it at the console or add the trace path twice.

Reuse an existing provider and exporter setup where possible. Instrumentation that patches libraries generally must initialize before those libraries load. Register once and drain the provider before process exit. Changing the application's existing export destinations is a separate decision; do not silently remove them.

## Classification

Telmoni reads OpenTelemetry GenAI semantic conventions. OpenInference attributes or legacy Vercel `ai.*` attributes alone do not identify model/tool operations. A generic span arriving successfully does not prove token/model/tool classification works. Check the [ingest contract](https://github.com/telmoni/telmoni/blob/main/web/content/docs/api/ingest.mdx) when implementing custom spans.

Prefer the explicit Telmoni SDK route when precise execution boundaries and content control are needed and framework instrumentation cannot supply them. The SDK's separate provider does not automatically pick up a framework's globally instrumented spans.

## Content and framework differences

Third-party instrumentation does not inherit the Telmoni SDK's privacy guarantees. Read the framework guide and the installed instrumentation's actual configuration. Some instrumentations transmit content by default; some emit messages only as logs, which Telmoni does not ingest. The project's content mode controls retention at ingest, not what a third-party exporter sends over the network.

Configure client-side content suppression when supported. If the integration cannot suppress content without losing required classification, disclose that limitation and choose a different route when the user requires metadata-only transmission. Never describe server-side dropping as keeping content inside the process.

Verify the real trace hierarchy, model/provider, usage, and content behavior after selecting the integration. Framework package availability and settings vary by version; do not transplant settings between different vendors' instrumentations.

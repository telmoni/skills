# Telmoni Skills

Agent skills for connecting applications and coding-agent sessions to [Telmoni](https://github.com/telmoni/telmoni), privacy-first, open-source monitoring for AI agents.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add telmoni/skills --skill telmoni
```

Or copy `skills/telmoni/` into your coding agent's supported skills directory. Install the entire folder so its references are available.

## Use

Paste this into your coding agent:

> Install the Telmoni skill from github.com/telmoni/skills and use it to add Telmoni tracing to this application, following best practices. Keep content capture off.

The skill helps the agent choose an SDK or an existing framework's OpenTelemetry integration, instrument executions and model/tool calls, configure the endpoint and API key, and verify the first trace. It supports Python, TypeScript/JavaScript, Go, and Rust through Telmoni's SDKs.

To monitor the coding agent itself, use this prompt instead:

> Install the Telmoni skill from github.com/telmoni/skills and help me install and configure the Telmoni observability plugin for my coding agent. Keep content capture off.

### Coding-agent plugins

You can also install a plugin directly, without installing this skill first. All three ship bundled JavaScript, need Node.js 22+, and record turns without changing application code.

| Agent | Manual setup | Plugin |
|---|---|---|
| Claude Code | Add marketplace, install, set the key with `/plugin configure`, start a new session | [Claude Code](https://github.com/telmoni/claude-code-observability-plugin) |
| Codex | Add marketplace, install, configure a private key file or environment, trust hooks in `/hooks` | [Codex](https://github.com/telmoni/codex-observability-plugin) |
| Antigravity | Install from GitHub, configure a private key file or environment; check App/IDE hooks if needed | [Antigravity](https://github.com/telmoni/antigravity-observability-plugin) |

Claude Code offers a built-in configuration UI for the key and endpoint. Codex and Antigravity bundle a `telmoni-observability` skill for setup, tagging, and troubleshooting; Claude Code bundles a `tag` skill. This repository's skill covers choosing and installing the appropriate plugin, including help before those bundled skills are available. See [plugin setup guidance](skills/telmoni/references/plugins.md).

You need a running Telmoni deployment and a project API key with the `ingest` scope (**Send spans** in the console). Configure credentials in the application's environment or the plugin's supported settings; do not paste API keys into prompts or committed files. The skill contains instructions, not credentials, an SDK, or runtime hooks.

Telmoni is self-hosted only, with no hosted service: use your deployment's machine endpoint, and the [source documentation](https://github.com/telmoni/telmoni/tree/main/web/content/docs).

## Maintain

The integration guidance is based on `telmoni/telmoni`'s SDKs and customer docs and the three plugin repositories. When updating it, check SDK signatures, lifecycle behavior, content handling, endpoints, and plugin installation/configuration against those sources. Keep examples aligned with the installed versions.

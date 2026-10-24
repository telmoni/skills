---
name: telmoni
description: >-
  Works with Telmoni, the platform that records AI agents' runs as metadata, for organizations and projects, members and roles, API keys, notifications and a hash-chained audit log: records an agent's runs with its SDKs (Python, TypeScript, Go, Rust) and a coding agent's own sessions with its plugin (Claude Code, Codex, OpenCode, Cursor), drives the `telmoni` CLI, calls the read-only `/v1` API with a `telmoni_` API key, builds and tests receivers for its signed webhooks, self-hosts it with Docker Compose or Kubernetes, and finds answers in its documentation. Use for any task that involves Telmoni or telmoni.com/docs, including when only the code or configuration names it (`TELMONI_API_KEY`, `TELMONI_ENDPOINT`, `Telmoni-Signature`).
license: Apache-2.0
allowed-tools:
  - WebFetch(domain:telmoni.com)
  - Bash(telmoni --version)
  - Bash(telmoni status *)
  - Bash(telmoni whoami *)
  - Bash(telmoni org list *)
  - Bash(telmoni config get *)
  - Bash(telmoni config list *)
---

# Telmoni

Telmoni records AI agents' runs as metadata — each run's steps, model and tool calls, tokens, timings and outcome, never a prompt or a completion — and runs the organizations and projects they belong to: members and roles, API keys, notifications to Slack and webhooks, a hash-chained audit log and a console agent. People use it through a web console, where a project's runs are read as traces, sessions and users, the `telmoni` CLI, the SDKs, the coding-agent plugins and a read-only HTTP API, on the hosted service at `https://telmoni.com` or on a deployment they run themselves. It has not launched, so its surface is small and changes often.

## Ground rules

1. **Docs before memory.** Telmoni changes faster than any model's training data. Fetch the relevant page before writing code or giving instructions, and take commands, fields and limits from it.
2. **Only what exists.** The API reads two things and writes nothing; the SDKs (Python, TypeScript, Go, Rust) record runs, steps, model calls and tool calls and send them to ingest at `/otlp/v1/traces`, which keeps a span only inside a run marked with `telmoni.run_id` and `telmoni.agent`, as the SDKs mark theirs and no stock exporter does; each installs from its language's registry. Telmoni sends no notice about a run and stops no agent; a project's runs are read in the console. When a task needs something the docs don't describe, say so and offer the nearest thing that exists; an invented route, flag, SDK method or event kind fails only once the user runs it.
3. **Most actions happen in the console.** Creating organizations and projects, inviting members, changing roles, minting, rotating and revoking API keys, connecting Slack or a webhook, and reading or exporting the audit log have no API or CLI command. Walk the user through the page that documents the action, at the console path it gives (such as `/{organization}/{project}/api-keys`).
4. **Secrets stay out of the conversation.** Never ask for an API key, a webhook signing secret or a `.env` file's contents, and never print, `cat` or log one: whatever reaches the transcript has leaked. Check presence instead (`[ -n "$TELMONI_API_KEY" ] && echo set`), and pass keys to commands through the environment, not as arguments.
5. **Know the endpoint.** The SDKs and the CLI default to `https://api.telmoni.com`. A self-hosted deployment is reached at its own machine host, named by `TELMONI_ENDPOINT` or, for an SDK client configured in code, its `endpoint` field, which the docs' examples set to `https://api.telmoni.com`: change it there too. A signed-in CLI keeps the endpoint it signed in to; a key in `TELMONI_API_KEY` takes `TELMONI_ENDPOINT`, then `telmoni config set endpoint`, on every command. When the code and environment don't settle which deployment the user means, ask: credentials from one never work on another.
6. **Without a shell** (a chat with no terminal, such as ChatGPT on the web), give the user each command to run and read what they paste back, and open documentation pages with whatever browsing or fetch tool you have.

## References

Read the one that matches the task before acting:

- driving the `telmoni` CLI (installing, signing in on a laptop, over SSH or in CI, scripting with `--json`, choosing an organization or a self-hosted endpoint): references/cli.md
- calling the `/v1` API, handling its errors and rate limits, rotating an API key, or using an SDK: references/api.md
- recording a coding agent's own sessions (Claude Code, Codex, OpenCode or Cursor, the one you run in included) with its plugin: references/coding-agents.md
- building, testing or debugging an endpoint that receives Telmoni webhooks: references/webhooks.md
- deploying, configuring, upgrading or operating a self-hosted Telmoni: references/self-host.md

## Documentation

Pages are at `https://telmoni.com/docs/<path>`, served by the console itself; fetch them with your web fetch tool. `https://telmoni.com/llms.txt` lists every page with its address and description, and `https://telmoni.com/llms-full.txt` is every page's text in one Markdown file. A self-hosted deployment serves the same three, for the version it runs, on its console's host (not a machine host of its own) and without the hosted service's `legal/` and `workspace/billing` pages.

| Topic | Paths |
|---|---|
| Introduction, signing in | the book's root (`/docs`), `getting-started/sign-in` |
| Self-hosting | `self-host/overview`, `self-host/docker-compose`, `self-host/kubernetes`, `self-host/agent`, `self-host/configuration`, `self-host/production` |
| Organizations, projects, members, roles | `workspace/organizations-and-projects`, `workspace/members`, `workspace/roles` |
| Traces, sessions, users: a project's runs in the console | `workspace/traces`, `workspace/sessions`, `workspace/users` |
| Audit log, billing on the hosted service | `workspace/audit-log`, `workspace/billing` |
| How long each kind of data is kept, and what a deletion removes | `workspace/data-retention`, `workspace/data-deletion` |
| Notifications, Slack, webhooks | `integrations/notifications`, `integrations/slack`, `integrations/webhooks` |
| CLI, SDKs, coding-agent plugins, this skill, API keys, ingest and what it keeps, API, errors | `api/cli`, `api/sdks`, `api/coding-agents`, `api/agent-skill`, `api/api-keys`, `api/ingest`, `api/field-inventory`, `api/reference`, `errors` |
| Account settings, accessibility, sessions, deletion | `account/settings`, `account/accessibility`, `account/privacy` |
| Legal, security, subprocessors, the two FAQs for a review | `legal/privacy-policy`, `legal/terms-of-service`, `legal/subprocessors`, `legal/security`, `legal/privacy-faq`, `legal/security-faq` |
| Contributing: how to, developing locally, the Code of Conduct, the AI policy | `contributing/introduction`, `contributing/developing`, `contributing/code-of-conduct`, `contributing/ai-policy` |

To find which page mentions a term (an environment variable, an error type, a header), search the text of the whole site; each match prints with the page it came from:

```bash
curl -s https://telmoni.com/llms-full.txt | awk -v q='<term>' '/^Source: /{src=$2} index(tolower($0), tolower(q)) {print src": "$0}'
```

A suspected vulnerability is reported privately, as `legal/security` describes, never in a public issue.

## Feedback on this skill

When the user says this skill gave wrong, outdated or missing guidance (as opposed to a problem with Telmoni itself), offer to draft an issue for `telmoni/skills`: what they were doing, what the skill said, and what was right. Show them the draft, and once they approve it, give them a link to open it themselves: `https://github.com/telmoni/skills/issues/new?title=<url-encoded title>&body=<url-encoded body>`. Leave out keys, tokens, email addresses and anything from a `.env` file.

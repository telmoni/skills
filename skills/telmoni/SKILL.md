---
name: telmoni
description: >-
  Works with Telmoni, the platform for organizations and projects, members and roles, API keys, notifications and a hash-chained audit log: drives the `telmoni` CLI, calls the read-only `/v1` API with a `telmoni_` API key, builds and tests receivers for its signed webhooks, self-hosts it with Docker Compose or Kubernetes, and finds answers in its documentation. Use for any task that involves Telmoni or telmoni.com/docs, including when only the code or configuration names it (`TELMONI_API_KEY`, `TELMONI_ENDPOINT`, `Telmoni-Signature`).
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

Telmoni runs organizations and their projects: members and roles, API keys, notifications to Slack, Discord and webhooks, a hash-chained audit log and a console agent. People use it through a web console, the `telmoni` CLI and a read-only HTTP API, on the hosted service at `https://telmoni.com` or on a deployment they run themselves. It has not launched, so its surface is small and changes often.

## Ground rules

1. **Docs before memory.** Telmoni changes faster than any model's training data. Fetch the relevant page before writing code or giving instructions, and take commands, fields and limits from it.
2. **Only what exists.** The API reads two things and writes nothing, the SDKs hold configuration and send no requests, and nothing ingests agent runs or traces yet. When a task needs something the docs don't describe, say so and offer the nearest thing that exists; an invented route, flag, SDK method or event kind fails only once the user runs it.
3. **Most actions happen in the console.** Creating organizations and projects, inviting members, changing roles, minting, rotating and revoking API keys, connecting Slack, Discord or a webhook, and reading or exporting the audit log have no API or CLI command. Walk the user through the page that documents the action, at the console path it gives (such as `/{organization}/{project}/api-keys`).
4. **Secrets stay out of the conversation.** Never ask for an API key, a webhook signing secret or a `.env` file's contents, and never print, `cat` or log one: whatever reaches the transcript has leaked. Check presence instead (`[ -n "$TELMONI_API_KEY" ] && echo set`), and pass keys to commands through the environment, not as arguments.
5. **Know the endpoint.** The SDKs use `https://telmoni.com` unless `TELMONI_ENDPOINT` names a self-hosted deployment's origin; the CLI chooses its endpoint at `login` (`--endpoint`, `TELMONI_ENDPOINT`, its `endpoint` setting, then that default) and keeps it until it signs in again. When the code and environment don't settle which one the user means, ask: credentials from one deployment never work on another.
6. **Without a shell** (a chat with no terminal, such as ChatGPT on the web), give the user each command to run and read what they paste back, and open documentation pages with whatever browsing or fetch tool you have.

## References

Read the one that matches the task before acting:

- driving the `telmoni` CLI (installing, signing in on a laptop, over SSH or in CI, scripting with `--json`, choosing an organization or a self-hosted endpoint): references/cli.md
- calling the `/v1` API, handling its errors and rate limits, rotating an API key, or using an SDK: references/api.md
- building, testing or debugging an endpoint that receives Telmoni webhooks: references/webhooks.md
- deploying, configuring, upgrading or operating a self-hosted Telmoni: references/self-host.md

## Documentation

Pages are at `https://telmoni.com/docs/<path>`, served by the console itself; fetch them with your web fetch tool. `https://telmoni.com/llms.txt` lists every page with its address and description, and `https://telmoni.com/llms-full.txt` is every page's text in one Markdown file. A self-hosted deployment serves the same three at its own origin, for the version it runs.

| Topic | Paths |
|---|---|
| Introduction, signing in | the book's root (`/docs`), `getting-started/sign-in` |
| Organizations, projects, members, roles | `workspace/organizations-and-projects`, `workspace/members`, `workspace/roles` |
| Audit log, billing on the hosted service | `workspace/audit-log`, `workspace/billing` |
| Notifications, Slack, Discord, webhooks | `integrations/notifications`, `integrations/slack-and-discord`, `integrations/webhooks` |
| CLI, SDKs, API keys, API, errors | `api/cli`, `api/sdks`, `api/api-keys`, `api/reference`, `errors` |
| Self-hosting | `self-host/overview`, `self-host/docker-compose`, `self-host/kubernetes`, `self-host/agent`, `self-host/configuration`, `self-host/production` |
| Account settings, accessibility, sessions, deletion | `account/settings`, `account/accessibility`, `account/privacy` |
| Legal, security, subprocessors | `legal/privacy-policy`, `legal/terms-of-service`, `legal/subprocessors`, `legal/security` |

To find which page mentions a term (an environment variable, an error type, a header), search the text of the whole site; each match prints with the page it came from:

```bash
curl -s https://telmoni.com/llms-full.txt | awk -v q='<term>' '/^Source: /{src=$2} index(tolower($0), tolower(q)) {print src": "$0}'
```

A suspected vulnerability is reported privately, as `legal/security` describes, never in a public issue.

## Feedback on this skill

When the user says this skill gave wrong, outdated or missing guidance (as opposed to a problem with Telmoni itself), offer to draft an issue for `telmoni/skills`: what they were doing, what the skill said, and what was right. Show them the draft, and once they approve it, give them a link to open it themselves: `https://github.com/telmoni/skills/issues/new?title=<url-encoded title>&body=<url-encoded body>`. Leave out keys, tokens, email addresses and anything from a `.env` file.

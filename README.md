# Telmoni Skills

[![CI](https://github.com/telmoni/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/telmoni/skills/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

[Agent Skills](https://agentskills.io) that teach coding agents (Claude Code, Codex and ChatGPT, OpenCode, Antigravity, Cursor and any other that reads `SKILL.md`) to work with [Telmoni](https://github.com/telmoni/telmoni): the `telmoni` CLI, API keys and the read-only `/v1` API, signed webhooks, and self-hosting. A skill sends the agent to [telmoni.com/docs](https://telmoni.com/docs) for the details and adds what the pages alone don't give it: which path fits which situation, the mistakes agents make, and the guardrails around keys and someone's infrastructure.

Telmoni has not launched yet, and the skills cover what a user can reach today.

## Skills

| Skill | What it does |
|---|---|
| [`telmoni`](skills/telmoni/SKILL.md) | Drives the CLI, calls the `/v1` API, builds and tests webhook receivers, self-hosts with Docker Compose or Kubernetes, and finds answers in the documentation. |

## Install

### Claude Code

```console
/plugin marketplace add telmoni/skills
/plugin install telmoni@telmoni
```

From a shell, the same is `claude plugin marketplace add telmoni/skills` and `claude plugin install telmoni@telmoni`. The skill loads by itself when a task involves Telmoni, and `/telmoni:telmoni` calls it by name. Claude Code doesn't update a third-party marketplace on its own: `claude plugin update telmoni@telmoni` fetches the latest, or turn on auto-update for it under `/plugin` → **Marketplaces**.

### Codex

```console
codex plugin marketplace add telmoni/skills
codex plugin add telmoni@telmoni
```

### Antigravity

The `agy` CLI installs a clone of this repository as a plugin, for the IDE and the CLI alike:

```console
git clone https://github.com/telmoni/skills.git telmoni-skills
agy plugin install ./telmoni-skills
```

`git pull` in the clone, then the same install again, brings a newer version.

### OpenCode, Cursor, Copilot, Gemini CLI and other agents

The [skills CLI](https://github.com/vercel-labs/skills) installs the skill into the agents it finds in your project; `-a <agent>` picks one (`opencode`, `antigravity`, `cursor`, `github-copilot`, `gemini-cli`, …), and `-g` installs it for your user instead:

```console
npx skills add telmoni/skills
```

### ChatGPT

The ChatGPT desktop app lists the skills of the projects you open in its **Skills** sidebar, so a project that holds the skill in `.agents/skills/` (`npx skills add telmoni/skills -a codex` puts it there) has it in ChatGPT too, and a skill linked into `~/.agents/skills/` follows you to every project. ChatGPT on the web and on mobile takes skills only from OpenAI's plugin directory; the Telmoni plugin is not listed there yet.

### By hand

Clone this repository and link the skill into your agent's skills directory: `~/.claude/skills/` for Claude Code, `~/.agents/skills/` for Codex, Cursor, Copilot, Gemini CLI and the ChatGPT desktop app, `~/.config/opencode/skills/` for OpenCode, `~/.gemini/config/skills/` for Antigravity.

```console
git clone https://github.com/telmoni/skills.git telmoni-skills
ln -s "$PWD/telmoni-skills/skills/telmoni" ~/.claude/skills/telmoni
```

## Before you start

- **Keys stay out of the chat.** Put an API key in `TELMONI_API_KEY`, or a webhook signing secret in your secret store, before you start; the skill has the agent check that a key is set, never ask for or print one.
- **Self-hosted?** Set `TELMONI_ENDPOINT` to your deployment's origin; without it, the CLI and SDKs talk to `https://telmoni.com`.
- **The CLI is optional:** the skill installs it when a task needs it, with your go-ahead.

## Layout

```text
skills/          one directory per skill: SKILL.md and its references/
evals/           the cases the skills are tested against, with and without them (claude plugin eval)
.claude-plugin/  the Claude Code plugin, and the marketplace that installs it
plugin.json      the Agent Plugins manifest, for Codex, Antigravity, Cursor, VS Code and Copilot, and its listing for OpenAI's plugin directory
Makefile         make check, the gate CI runs; make eval, the eval suite
```

## Contributing

How to contribute, the AI policy, the Code of Conduct and the security policy are in the docs: [telmoni.com/docs/contributing](https://telmoni.com/docs/contributing/introduction). [`AGENTS.md`](AGENTS.md) holds the rules every change to a skill is held to, and how to test one. A skill that gave an agent wrong guidance is an [issue here](https://github.com/telmoni/skills/issues); a problem with Telmoni itself goes to the repository concerned, as [SUPPORT.md](https://github.com/telmoni/.github/blob/main/SUPPORT.md) lists.

## License

Apache-2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). Unless you say otherwise, a contribution you submit is licensed the same way.

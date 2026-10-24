---
description: Record a coding agent's own sessions, the one you run in included, with Telmoni's plugin for Claude Code, Codex, OpenCode or Cursor — which plugin, its install, where its key goes and never through you, what it never sends, and its log.
---

# The coding-agent plugins

Fetch https://telmoni.com/docs/api/coding-agents before proposing anything: it has each plugin's install lines, key and log. A plugin records each turn of the agent it is installed in as one run, and the agent's session as the run's session, so a project's **Sessions** page reads a session as its traces. A run holds the models called with their tokens, each tool call by name, time and outcome, each subagent (in Codex, whose subagents' turns are runs of their own), and in Claude Code the names of the skills the turn ran. A plugin never sends a prompt, a reply, the model's thinking, a command, a tool's input or output beyond such a skill's name, the path or contents of a file the user works on, or the working folder; tell the user so before they decide.

| Agent | Plugin | Its runs' agent |
|---|---|---|
| Claude Code | `telmoni/claude-observability-plugin` | `claude-code` |
| Codex | `telmoni/codex-observability-plugin` | `codex` |
| OpenCode | `telmoni/opencode-observability-plugin` | `opencode` |
| Cursor | `telmoni/cursor-observability-plugin` | `cursor` |

## Which plugin

- "Record this session" means the plugin of the agent you run in. Cursor runs Claude Code's hooks too, but the Claude Code plugin does nothing there: in Cursor, it is Cursor's plugin.
- Never wire an agent's hooks to an SDK, or write a hook of your own: a hook is handed the person's prompts and files, and the plugin keeps only what the page names. The SDKs record the agents a user builds.
- This skill sends nothing, and is not the plugin: the skill is `telmoni@telmoni`, the plugin `telmoni-observability@telmoni-plugins` in Claude Code and Codex, and installing one never brings the other.

## Installing

- Each is the npm package named as its repository is (`@telmoni/claude-observability-plugin`), installed with the page's lines, or a build from a checkout of its repository; a plugin package outside the `@telmoni` scope is not Telmoni's.
- Give the user the lines, and run none of them until they say go: from then on the plugin runs at every turn and sends Telmoni each one's metadata. That covers a clone or a build, `npm install -g`, a `claude plugin`, `codex plugin`, `opencode plugin` or `telmoni-cursor-observability setup` command, and an edit to `opencode.json`.
- Claude Code's, Codex's and Cursor's plugins need Node.js 22.23.4, 24.22.1, 26.12.1 or later (October 2026's security releases) with npm on the `PATH`; Claude Code and Codex need git, with which they add a plugin's marketplace, and Codex needs 0.143 or later; OpenCode's runs inside OpenCode, 1.18.29 or later, or 2.
- Nothing is recorded before the agent loads the plugin: Claude Code loads it as a session starts, Codex and OpenCode as they start, so the user starts a new session, or restarts Codex or OpenCode, once it and its key are in; Cursor reloads its hooks file as it changes, so its next prompt is recorded.
- Codex runs a plugin's hooks only once the user trusts them, when Codex asks or in `/hooks`; `codex exec` asks nothing, so they trust them once in Codex itself.
- A turn is sent once it has ended, so the one in progress shows only after it; Codex may end one minutes after its answer, while another plugin's hooks run or it compacts the session.

## The key

- A project API key holding only the **ingest** scope (**Send spans**), minted on the console's `/{organization}/{project}/api-keys` page: its project is where the sessions land.
- The key goes into the plugin's own setup, which the user does: in Claude Code, `/plugin configure telmoni-observability@telmoni-plugins`, or, from a checkout, `TELMONI_API_KEY` in the environment Claude Code starts in; for Cursor, `telmoni-cursor-observability setup`, which asks for it or takes `TELMONI_API_KEY`; for Codex and OpenCode, a `telmoni.json` the user writes (`~/.codex/telmoni.json`, or under `CODEX_HOME`; `~/.config/opencode/telmoni.json`, or under `OPENCODE_CONFIG_DIR` or `XDG_CONFIG_HOME`), or `TELMONI_API_KEY`. Codex's, OpenCode's and Cursor's plugins read their key file only while the user owns it and group and others have no access (`chmod 600` does it), a field in it empty or no string refused; past one they pass over they send nothing, a key in the environment or not, unless `TELMONI_API_KEY` and `TELMONI_ENDPOINT` are both set, when the file is not read, and the log says why. Never ask for the key, read it, print it or write it: check presence and mode instead (`[ -n "$TELMONI_API_KEY" ] && echo set`; `ls -l "${CODEX_HOME:-$HOME/.codex}/telmoni.json"`).
- Cursor's cloud agents read only the repository's hooks: `telmoni-cursor-observability setup --project` writes a `.cursor/hooks.json` to commit, which holds no key, runs the package's command from the `PATH`, so cloud agents need the package installed by `.cursor/environment.json`'s install step (`npm install -g @telmoni/cursor-observability-plugin`), and runs on teammates' machines too; the key is the Cloud Agents secret `TELMONI_API_KEY`.
- A self-hosted Telmoni is reached at its own machine host, through `TELMONI_ENDPOINT` or the plugin's own endpoint setting, over HTTPS: the SDK inside refuses plain `http://` to any host but this machine.

## When nothing shows up

- Each plugin writes what went wrong to a log of its own, never anything said in the session: `~/.claude/telmoni/hook.log`, `~/.codex/telmoni/hook.log`, `~/.cursor/telmoni/hook.log` or `~/.local/state/telmoni/opencode/plugin.log` (`CLAUDE_CONFIG_DIR`, `CODEX_HOME` and `XDG_STATE_HOME` move them). It says when no key is set, and gives Telmoni's answer to a turn it refused: `401` for a dead key, `403` `/errors/authz/forbidden` for one without the **ingest** scope. Each also gives, once, the SDK's reason for refusing the endpoint (`endpoint refused by the SDK`). Read it before guessing.
- A turn Telmoni did not take — out of reach, busy, its database failing it (`500` `/errors/internal/database`), or its key refused — is sent again as a later turn of the same session ends, the session's later turns waiting for it; OpenCode's plugin holds such turns in memory, trying them every five minutes and at any session's next turn (on OpenCode 1, any in the same folder), and loses any still unsent three seconds into its shutdown. One Telmoni took in part, or refused for good — `400` or `413` for what it holds, `402` for a paused organization, any other `500`, and in OpenCode, which reads its key only as it loads, `401` and `403` too — is logged and not sent again. Where the server reaches its Redis, a copy that lands within the hour is stored once.

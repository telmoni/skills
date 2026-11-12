# Coding-agent plugins

Record the coding agent's own sessions in Telmoni. The plugin is a set of hooks that run as each turn ends; this workflow installs and diagnoses it. No application code or SDK dependency changes.

## Contents

- [Before starting](#before-starting)
- [Claude Code](#claude-code), [Codex](#codex), [Antigravity](#antigravity)
- [Settings that travel with the key](#settings-that-travel-with-the-key)
- [Confirm and diagnose](#confirm-and-diagnose)
- [Tags](#tags)
- [Report](#report)

## Before starting

- Work on the one agent the user wants monitored.
- All three plugins need Node.js 22+ on the `PATH` the agent starts with, and a project API key with the `ingest` scope (**Send spans**). Claude Code and Codex also need git.
- The plugins ship their own bundled JavaScript: no `npm install`, no build.
- **The key is the user's alone.** Never ask for it in chat, accept one pasted there, put one in a command you run, or open, print, copy or write the file that holds it. Tell the user what to run in their own terminal.
- If a command below is refused, check the installed agent's version and `--help` before trying anything else. Never hand-write hooks in place of a working plugin install.

Each agent follows the same four steps: install, set the key, activate, confirm.

## Claude Code

1. **Install.**

   ```sh
   claude plugin marketplace add telmoni/claude-code-observability-plugin
   claude plugin install telmoni-observability@telmoni-plugins
   ```

2. **Key.** The user sets the key, and the endpoint for their own deployment, inside Claude Code:

   ```text
   /plugin configure telmoni-observability@telmoni-plugins
   ```

   Claude Code keeps the key with its own credentials. Leave **Capture content** off and both scrubbers on.
3. **Activate.** Start a new session: plugins load as a session starts.
4. **Confirm**, as under [Confirm and diagnose](#confirm-and-diagnose).

A `TELMONI_API_KEY` in the environment Claude Code starts in wins over the plugin's settings, and takes its endpoint and switches from that environment too. Update with `claude plugin update telmoni-observability@telmoni-plugins`, then start a new session. For one session from a clone, the [README](https://github.com/telmoni/claude-code-observability-plugin#from-a-checkout) documents `claude --plugin-dir`; prefer the marketplace install.

## Codex

Needs Codex 0.167 or later.

1. **Install.**

   ```sh
   codex plugin marketplace add telmoni/codex-observability-plugin
   codex plugin add telmoni-observability@telmoni-plugins
   ```

2. **Key.** The user creates the key file in their own terminal: `~/.codex/telmoni.json` (under `CODEX_HOME` where that is set), owned by them and mode `600`. They run this, type `{"apiKey": "tm_…"}`, press Enter, then Ctrl-D, so the key never reaches shell history:

   ```sh
   (umask 077 && cat > ~/.codex/telmoni.json) && chmod 600 ~/.codex/telmoni.json
   ```

   For their own deployment they add `"endpoint"` beside the key. If the file exists already, they edit it rather than overwrite it.
3. **Activate.** The user starts Codex, runs `/hooks`, and trusts the plugin's `Stop` and `SessionEnd` hooks. Only the user can do this; never report it done on their behalf. `codex exec` cannot grant trust.
4. **Confirm**, as under [Confirm and diagnose](#confirm-and-diagnose).

`TELMONI_API_KEY` and `TELMONI_ENDPOINT` in `~/.codex/.env` work too and win over the key file. A key exported in the shell may not reach an interactive session, whose background service keeps the environment it first started with; the key file avoids that. `codex exec --ephemeral` keeps no rollout and is never recorded.

Update with `codex plugin marketplace upgrade telmoni-plugins`, add the plugin again, and have the user trust the hooks again: Codex asks after every update.

## Antigravity

1. **Install.**

   ```sh
   agy plugin install https://github.com/telmoni/antigravity-observability-plugin
   ```

2. **Key.** As for Codex, in the user's own terminal, at `~/.gemini/config/telmoni.json`:

   ```sh
   (umask 077 && cat > ~/.gemini/config/telmoni.json) && chmod 600 ~/.gemini/config/telmoni.json
   ```

   `TELMONI_API_KEY` and `TELMONI_ENDPOINT` in the environment `agy` starts in work too, and win over the file.
3. **Activate.** Start a new session.
4. **Confirm**, as under [Confirm and diagnose](#confirm-and-diagnose).

The plugin's hooks are listed for the CLI. If App or IDE sessions do not appear, follow the [README's App and IDE section](https://github.com/telmoni/antigravity-observability-plugin#the-antigravity-app-and-ide): merge its one documented entry into `~/.gemini/config/hooks.json`, keeping every hook already there. Where both run, each turn is still sent once. Update by installing again.

## Settings that travel with the key

The key, the endpoint and the switches always come from one place together: a plugin never pairs a key from the environment with an endpoint or a switch from a file, or the reverse.

| Setting | Claude Code (`/plugin configure`) | Codex, Antigravity (key file) | Beside a key in the environment |
|---|---|---|---|
| Endpoint | **Telmoni endpoint** | `"endpoint"` | `TELMONI_ENDPOINT` |
| Content, off by default | **Capture content** | `"captureContent": true` | `TELMONI_CAPTURE_CONTENT=1` |
| Secrets scrubber, on by default | **Scrub secrets** | `"scrubSecrets": false` turns it off | `TELMONI_SCRUB_SECRETS=0` turns it off |
| Personal-data scrubber, on by default | **Scrub personal data** | `"scrubPii": false` turns it off | `TELMONI_SCRUB_PII=0` turns it off |

- The endpoint is the deployment's machine endpoint as a base URL, not the console's URL and not the ingest path. It has no default: left out, the plugin records nothing (see *Availability* in the skill).
- Content needs the local switch **and** the project's content mode `on`. Never turn it on to fix missing traces: traces are sent without it.
- Leave both scrubbers on unless the user asks otherwise. The plugins scrub personal data by default; the SDKs do not.

## Confirm and diagnose

Have the user finish one normal turn in a new session, then look at the project's **Traces** page for the agent `claude-code`, `codex` or `antigravity`. A trace is sent as a turn ends, never on install, so installing proves nothing. A Codex turn that was interrupted or failed is sent at the next turn's end or the session's; a Claude Code background subagent can delay its turn.

If nothing appears, check in this order:

1. The plugin is installed and enabled (`claude plugin list`, `codex plugin list`).
2. Codex only: `/hooks` shows the plugin's hooks trusted.
3. `node --version` prints 22 or later in the shell the agent starts from.
4. The plugin's `hook.log`, its last lines only:

   | Agent | Log |
   |---|---|
   | Claude Code, marketplace install | `~/.claude/plugins/data/telmoni-observability-telmoni-plugins/hook.log` |
   | Codex | `~/.codex/plugins/data/telmoni-observability-telmoni-plugins/hook.log` |
   | Antigravity | `~/.gemini/config/telmoni/hook.log` |

   No log means the hook never ran: go back to 1 to 3. `no key`, a key file passed over, a refused endpoint, `401` or `403` are configuration, which the user fixes. A turn held or kept is sent again later: address the cause the line names, and do not reinstall in a loop.

Read the log only. Never read transcripts, pending-turn files or the key file. A custom agent home, or Claude Code's `--plugin-dir`, moves these paths: see the plugin's README.

Once a plugin is installed, its own bundled skill covers day-to-day help: `telmoni-observability` in Codex and Antigravity (setup, tags, troubleshooting), `tag` in Claude Code.

## Tags

Prefer the plugin's own skill. A `.telmoni-tags.json` in the folder the agent starts in labels every turn, such as `{"repo": "telmoni", "branch": "main"}`. Tags are sent in every content mode and everyone on the project sees them: no secret, no personal detail, nothing taken from a private path. The file does not follow a branch switch.

## Report

Name the plugin installed or found, the prerequisites checked, the steps still the user's (the key, Codex's hook trust), and whether a trace was actually seen. Never call the plugin active while one of those is open.

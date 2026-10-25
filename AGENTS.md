# Telmoni Skills — Agent Guidelines

The agent skills for Telmoni ([`telmoni/skills`](https://github.com/telmoni/skills)): instructions that coding agents (Claude Code, Codex, Cursor and any other that reads `SKILL.md`) load to work with Telmoni on a person's behalf. Every skill restates what the platform and its SDKs ([`telmoni/telmoni`](https://github.com/telmoni/telmoni)) and the CLI ([`telmoni/telmoni-cli`](https://github.com/telmoni/telmoni-cli)) do, and routes the agent to the docs at [telmoni.com/docs](https://telmoni.com/docs) (the book, [`telmoni/docs`](https://github.com/telmoni/docs)) for the rest; those repositories are the authority on everything written here. The repository is public, and every file in it is published as written.

## Ground Rules
- **Pre-launch:** nothing has shipped. Rename, restructure and rewrite skills to their ideal state; no deprecated names, redirects or migration notes.
- **Quality gate:** never leave the tree broken: every install clones `main` as it stands.
- **Ask first:** a new skill, a new top-level directory, any change to a skill's `allowed-tools`, any dependency (a GitHub Action, a tool CI or the `Makefile` installs), and any external-state change (publishing to a marketplace, a release, a call to a live Telmoni with a real key).
- **Cover only what a user can reach**, as the docs do: signing in, the CLI and SDKs, the coding-agent plugins, API keys and the read-only `/v1` API, errors, notifications and connectors, organizations, projects, members, roles and the audit log, and self-hosting. Never anything not built yet: a capability gets a reference once a user can reach it, never ahead of it.
- **Public sources only:** a skill states nothing beyond what telmoni.com/docs and the public repositories already state.

## Where Things Live
| Path | What |
|---|---|
| `skills/<name>/SKILL.md` | A skill: its frontmatter (`name`, `description`, `license`, `allowed-tools`; nothing outside the Agent Skills spec) and the body every invocation loads. |
| `skills/<name>/references/` | One file per use case, opened only when `SKILL.md` routes there. |
| `evals/<case>/` | One case for `claude plugin eval`: `prompt.md` (the request as a person would type it, and its run limits), `graders/` (the checks), and for a case that needs a starting project, `case.yaml` and `scaffold.sh`. |
| `evals/codex.py` | The same cases run in Codex, headless (`codex exec`), with the skill linked into each run's project and without, graded by the same graders: `make eval-codex`. |
| `.claude-plugin/` | `plugin.json`, the Claude Code plugin, and `marketplace.json`, which makes this repository its own marketplace; Codex and Copilot read that marketplace too. |
| `.codex-plugin/` | `plugin.json`, the Codex manifest for releases before 0.146, which read no root `plugin.json`; its `interface` is a copy of `plugin.json`'s `extensions["com.openai"].interface`, which later releases read instead. |
| `.cursor-plugin/` | `plugin.json`, the Cursor plugin manifest, checked against Cursor's schema. |
| `plugin.json` | The [Agent Plugins](https://agent-plugins.org) manifest, which Codex prefers and Antigravity, Cursor, VS Code and Copilot read; its `extensions["com.openai"]` block is the listing OpenAI's plugin directory shows ChatGPT users. |
| `Makefile` | `check`, the gate; `eval`, the eval suite in Claude Code; `eval-codex`, the same in Codex. |
| `.github/workflows/ci.yml` | CI: `make check` and actionlint. |
| `scratch/` | The maintainer's notes, gitignored. Never write to it. |
| [`telmoni/telmoni`](https://github.com/telmoni/telmoni) | Sibling repo, checked out as `../telmoni`: the platform and the four SDKs under `sdk/`, the authority on the API, the SDKs, webhooks, errors and self-hosting, and the console that serves the book. |
| [`telmoni/docs`](https://github.com/telmoni/docs) | Sibling repo, checked out as `../docs`: the book, `content/`, which every console serves at `/docs`, and the hosted service's own pages (billing, legal), `hosted/`, which telmoni.com/docs serves beside it: the pages every skill links to. |
| [`telmoni/telmoni-cli`](https://github.com/telmoni/telmoni-cli) | Sibling repo, checked out as `../telmoni-cli`: the CLI, and the authority on its commands, flags and variables. |

## Commands
- **After every change** (no permission needed; report failures verbatim): `make check`, which validates each skill against the Agent Skills spec (`skills-ref`), `plugin.json` against the Agent Plugins schema, `.cursor-plugin/plugin.json` against Cursor's, and the Claude Code plugin and marketplace (`claude plugin validate .`). It needs `uv` and Claude Code. Its one expected warning is the missing `version` (Versioning).
- **Only when asked**, since it spends model usage: `make eval`, or one case with `make eval CASE=<case> RUNS=1`. On Linux the runs need `bubblewrap` and `socat` for Claude Code's sandbox. `make eval-codex` runs the cases in Codex the same way; it needs Codex (`npm install -g @openai/codex`) signed in. Unasked, say "untested" and name the command.
- **Locally:** `claude --plugin-dir .` starts a Claude Code session with this checkout's plugin loaded. `agy plugin install .` installs it into Antigravity; `agy plugin validate` reads only `plugin.json`, so it is no check of a skill and is not in the gate.

## Writing Rules
Read every file as its runtime reader does: an agent in the middle of someone's task, wanting to act. A line it cannot act on, or would have known anyway, is noise that dilutes the rest.
- **Beat the docs, or add nothing.** An agent can fetch any page itself. A skill adds the decision (which path for which situation), the trap (what agents get wrong), the guardrail (secrets, someone's infrastructure) and where to look; restating a page is maintenance that goes stale.
- **Link, don't copy.** Link the served page (`https://telmoni.com/docs/integrations/webhooks`) so the agent reads the current version. No code samples: the docs carry them, in step with the platform. A command line, a header or a field name is fine.
- **Routing lives in exactly two places:** one line per reference in `SKILL.md`'s `## References` list, and that reference's frontmatter `description`. No "when to use" prose anywhere else; a reference body is read only after the agent chose it.
- **Leave a skill's `description` alone** unless the skill's scope changes. It only decides whether the skill loads at all; routing inside the skill is the body's job.
- **Every line earns its place.** A reference is at most 100 lines, frontmatter included, and `SKILL.md` stays far below the 500-line ceiling. Cut filler, hedging, restatement and anything an agent infers alone.
- **Give the reason, not the volume.** One clause of why ("a parsed body no longer matches the signature") steers an agent better than ALWAYS or NEVER in capitals.
- **Verify against source before writing:** every command, flag, variable, header, route, status code, limit and retry schedule, in `telmoni/telmoni` or `telmoni/telmoni-cli`, and every page you link. The live site can lag the code.
- **Claim only what a diff could disprove:** describe mechanisms, never outcomes ("tamper-resistant", "secure", "guaranteed").
- **`allowed-tools` lists only no-brainers:** fetching telmoni.com, and CLI commands that read (`telmoni --version`, `status`, `whoami`, `org list`, `config get`, `config list`). A tool not listed still runs after one prompt; an auto-allow a person would hesitate over keeps them from installing the skill.
- **Secrets never pass through a conversation:** a skill has the agent check a key by its presence, never read, print or ask for one, and the same for `whsec_` secrets and `.env` files.
- **Every skill carries `license: Apache-2.0`** in its frontmatter: an install copies the skill's directory without this repository's `LICENSE`.

## Contracts
These files restate code and pages; when those change, the skill follows. Every `.mdx` named here is under `content/` in `telmoni/docs`.
- `skills/telmoni/SKILL.md`, the documentation table: the book's sidebar as telmoni.com/docs serves it, the `meta.json` files under `content/` in `telmoni/docs` with the hosted service's own pages (`hosted/`: billing, legal) beside them.
- `references/cli.md`: commands, flags, variables and output in `src/` of `telmoni/telmoni-cli`, and `api/cli.mdx`.
- `references/api.md`: `crates/auth/src/handler/v1.rs`, `crates/auth/src/handler/tokens.rs`, the machine host's door (`crates/telmoni/src/door.rs`), ingest (`crates/telemetry/src/handler/ingest.rs` and `crates/telemetry/src/contract.rs`), the error types in `crates/shared/src/error.rs` and `sdk/` in `telmoni/telmoni`, and `api/reference.mdx`, `api/ingest.mdx`, `api/field-inventory.mdx`, `api/api-keys.mdx`, `api/sdks.mdx` and `errors.mdx`.
- `references/webhooks.md`: `crates/notifications/src/connector/webhook.rs`, `crates/notifications/src/delivery.rs` and `web/lib/webhook-signature.ts` in `telmoni/telmoni`, and `integrations/webhooks.mdx`.
- `references/self-host.md`: `deploy/`, `crates/telemetry/clickhouse/`, `crates/migrator/sql/role_hardening.sql` and the binary's subcommands (`crates/telmoni/src/cli.rs`) in `telmoni/telmoni`, and the `self-host/` pages.
- `references/coding-agents.md`: `README.md`, `ARCHITECTURE.md` and `src/` of the four `telmoni/<agent>-observability-plugin` repositories, and `api/coding-agents.mdx`.
- `evals/`: the same sources as the reference each case exercises; a grader that pins a fact (the webhook test vector, an error type) changes with it.

## Versioning
No manifest carries a `version` before launch. Claude Code then versions the plugin by commit, so an update always brings the latest skills, where a `version` left unbumped would pin every user to the copy they first installed. That is why `claude plugin validate` warns and `make check` runs it without `--strict`. At launch, if releases should be pinned, every manifest — `.claude-plugin/plugin.json`, `plugin.json`, `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json` — gets the same `version` (never the marketplace entry), and every change to what a skill does bumps them all.

## Testing a Change
A skill is tested on the agents it ships to: a sentence that reads clearly in a diff can still steer an agent wrong mid-task.
- While iterating, `make eval CASE=<case> RUNS=1`; before a change counts as done, the cases it touches at the default three runs. Each case runs with and without the plugin, and `Δ` is what the skill adds. Read the transcripts in the report as well as the scores: which reference the agent opened, what it fetched, what it invented.
- A new reference or changed routing gets a case whose prompt should route there, phrased as a person would type it, and the other cases must still route where they did. Never tune a `description` to the cases' wording: a skill that passes only its own prompts has learned the prompts.
- Codex reads the same files and behaves differently: run the changed cases in Codex too, `make eval-codex CASE=<case> RUNS=1`, and compare its transcripts under `evals/results/` with Claude Code's. A `tool_used` grader there reads Codex's items (`Bash` its commands, `Write` and `Edit` its file changes), `Skill` fires where the skill's `SKILL.md` was read, and an `llm` grader is judged by Codex.
- A grader that reads a file names it by path, so the prompt names the files it expects the agent to write.

## Agent Hygiene
- **This repo only:** change nothing in another repository (`telmoni/telmoni`, `telmoni/telmoni-cli`, any other) unless the user says so for this task; that binds subagents too. Reading is fine.
- Edit `AGENTS.md` (`.github/copilot-instructions.md` points here) only when the user asks outright; otherwise propose a diff. There is no `CLAUDE.md`: Claude Code reads this file, and a `CLAUDE.md` at a plugin's root fails `claude plugin validate --strict`.
- No AI signatures anywhere, skills included.
- Comments in a grader or a script are for a person reading it, and short: they say *why*, never *what*, in a line or two at most.
- No scripted bulk edits: edit each file deliberately and review the diff. One-off scripts, eval workspaces and logs go in `/tmp/telmoni/`.
- Never read, print or copy a `.env` file or the CLI's saved login, the Keychain item `telmoni` on a Mac and its credentials file, and never put a real key in a skill, an eval or a commit.
- Keep the repo slim: fix a real problem where it lives. No guard script, lint gate or CI job for a problem that is not happening.

## Git Rules
- Commit only when asked: never `git add` or `git commit` unprompted.
- Conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `chore:`) of 1–5 lines and the sign-off: a subject, then optionally a blank line and up to 3 lines on *why*. No file lists, test output, AI signatures or `Co-authored-by` trailers.
- Every commit is signed off by the developer it is made for, certifying the [Developer Certificate of Origin](https://developercertificate.org/): `git commit -s` adds `Signed-off-by: Name <email>` from git's `user.name` and `user.email`, which name a person, never an agent. A merge commit too: a branch is merged in a clone, `git merge --no-ff --signoff`, and pushed, never from GitHub's merge button, whose commit carries none.
- No branches, worktrees, pushes or pull requests.

## Definition of Done
- [ ] `make check` passes, or the failure is reported verbatim.
- [ ] Every fact on a changed skill file was checked against current source, and every page it links resolves.
- [ ] A change to what a skill does ran through the eval cases it touches, or is reported "untested" with the `make eval` command.
- [ ] Nothing that needs asking happened unasked (a new skill, `allowed-tools`, dependencies, external state, other repos, commits).

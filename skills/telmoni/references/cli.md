---
description: Install and drive the `telmoni` CLI — sign in on a laptop, over SSH, in CI or a container, script it with `--json`, choose an organization or a self-hosted endpoint, and diagnose a failed sign-in.
---

# The telmoni CLI

Every command, flag, variable and output field is on https://telmoni.com/docs/api/cli. The CLI signs in and out, reports who it is signed in as, and chooses an organization; beyond its own session, it changes nothing on the server, except that `login`, `status` and `org switch` have the server provision a first organization for a person who belongs to none, as a console sign-in does.

## Install

Run `telmoni --version` first. If it's missing, the installer on the CLI page serves Apple-silicon macOS and x86_64 Linux with glibc; on an Intel Mac, ARM64 Linux or Alpine, build from source with the page's `cargo install` line instead. In a non-interactive shell, set `TELMONI_INSTALL_DIR` to an existing, writable directory: otherwise the installer calls `sudo` or `doas`, even to create `~/.local/bin`. The CLI is on no package registry, so a `telmoni` package found on one is not Telmoni's.

## Sign in: choose by where it runs

| Where | How |
|---|---|
| The user's own machine | Ask the user to run `telmoni login` in their own terminal and approve the code on the page it opens; continue once they say it finished. |
| SSH, a container, no browser | The same with `telmoni login --no-browser`; the user opens the printed address on any machine. |
| CI, servers, scripts | An API key in `TELMONI_API_KEY`: each command uses it and saves nothing, so no `login` is needed, and the key never goes on the command line. |

- `telmoni login` prints a one-time code and an address, then blocks, polling for up to ten minutes until a person approves the code. Started in your foreground shell, nobody sees the code, and a tool timeout kills it with nothing saved. If the user wants you to drive it, start `telmoni login --no-browser` in the background with its output going to a file, relay the code and address it prints (they are meant to be shown), and wait for it to exit 0.
- While `TELMONI_API_KEY` holds a key, even a stale one, every command that acts with a key uses it ahead of the saved login; `login`, `logout` and `org` say so on stderr. A blank value counts as unset.
- A key is checked only for its shape (`telmoni_…`); `telmoni status` is what proves it works.
- A key reaches only the API: `status` works, while `org list` and `org switch` need a device sign-in.
- To save a key instead, pipe it to `telmoni login --with-key` from a file or a secret store, never as an argument; it refuses a terminal. To fetch one from a secret manager for each command, the user sets `telmoni config set api_key_helper '<command>'`, a command that prints the key. Signing in again replaces the saved credentials without ending the earlier session; `telmoni logout` first ends it.

## Script it

- `telmoni status --json` is the machine interface. Branch on `authType` before reading anything else: `device` carries `person` and `activeOrganization` (`organizationId`, `slug`, `label`, `role`, or `null`), `api_key` carries `organization` and `keySource` (`environment`, `helper` or `saved`).
- Judge a run by its exit code: 0 for success, 1 for any failure (the reason is on stderr), 2 for a usage error. Signed out, plain `status` still prints `Endpoint: …` to stdout before failing, while `--json` prints nothing.
- `org list` has no JSON form. Each line is `<* or space> <id>  <slug>  <label>  <role>`, the fields two spaces apart; a label can contain spaces, so read the role from the right. It shows the list saved by the last `login`, `status` or `org switch`.
- Name organizations by ID (`org_…`). A slug moves when its organization's URL changes, and the CLI matches slugs exactly against its saved list, without asking the server.
- `TELMONI_ORG=<id> telmoni status` acts in another organization for one command without switching; device sign-ins only.
- Run `telmoni` commands one at a time: each may rotate the saved refresh token, and nothing locks the saved login between processes.

## Self-hosted endpoints

The endpoint is chosen at `login`, from `--endpoint`, then `TELMONI_ENDPOINT`, then `telmoni config set endpoint`, then `https://telmoni.com`. A saved session keeps the endpoint it signed in to, so moving to another deployment means `telmoni logout`, then `telmoni login --endpoint <origin>`. The CLI sends credentials only over HTTPS, except to localhost or a loopback address, which it reaches past any proxy.

## When it fails

- `-v` after the subcommand (`telmoni status -v`) logs to stderr where the CLI read and wrote the saved login and each request's method, address and status, never a header, token or key; at `login` it also says where the endpoint came from.
- `session ended; run telmoni login` means the session was ended (signed out elsewhere, ended from **Active sessions**, or 30 days unused) and the CLI already deleted its credentials: the user signs in again.
- The CLI needs network access to the endpoint and must write refreshed tokens to the Keychain on a Mac, else to its configuration directory; in a sandbox that blocks the write, a refresh it cannot save ends the session.
- Behind a proxy that intercepts TLS, certificate errors follow: the CLI trusts only its bundled root certificates, not the system store or `SSL_CERT_FILE`.
- Never open, print or copy the saved login: on a Mac the Keychain item `telmoni`, elsewhere the credentials file (`telmoni/credentials.json` in the user's configuration directory), which holds a refresh token or an API key unencrypted. `telmoni status` says what it holds.

---
type: llm
focus:
  source: file
  path: .github/workflows/telmoni-key.yml
---

PASS if all of these hold: the key reaches the job only through `env` (such as `TELMONI_API_KEY: ${{ secrets.TELMONI_API_KEY }}`), never as `${{ secrets.TELMONI_API_KEY }}` inside a `run:` script; the job proves the key with a server call (`telmoni status`, or a request to `/v1/organization`) rather than trusting `telmoni login`, which checks only the key's shape; when it uses the CLI's JSON, it reads the organization from `.organization`, not `.activeOrganization`; it runs no `telmoni org` command; it calls the API with curl, or installs the CLI with the CLI page's installer (x86_64 Linux; `TELMONI_VERSION` may pin it) or its `cargo install --locked telmoni-cli` line; and nothing prints the key.
FAIL if any one of these fails.

---
description: Self-host Telmoni — choose Docker Compose or the Helm chart, write its environment and secrets, start, verify and upgrade it, set up sign-in, the console agent and production hardening, and run the operator subcommands.
---

# Self-hosting Telmoni

Start at https://telmoni.com/docs/self-host/overview, then follow the page for the method: `self-host/docker-compose` for one host, to evaluate or serve a small company; `self-host/kubernetes` for the Helm chart. `self-host/configuration` lists every variable the server and console read (the Compose stack's own, such as `POSTGRES_PASSWORD` and the image tags, are on `self-host/docker-compose`), and `self-host/production` covers OIDC, database roles, partition rotation, backups and what the server refuses at boot.

## Before changing anything

- Starting, stopping or deleting a stack, `helm install` or `upgrade`, `kubectl apply`, and DNS, TLS or cloud KMS changes alter the user's infrastructure: say what will run and wait for a yes. `docker compose … down -v` deletes every organization's data.
- The published images (`ghcr.io/telmoni/server`, `ghcr.io/telmoni/web`) are `linux/amd64` only.
- On Compose every module connects as the database superuser, which row-level security does not bind. Production runs the per-module roles that `self-host/production` sets up.

## Docker Compose

- The compose file works only inside a clone of `telmoni/telmoni`, which it mounts files from, and reads `deploy/compose/.env`. Write that file from scratch with the keys the Compose page lists: the repository's root `.env.example` belongs to the development stack and points at services this one doesn't run.
- Generate each secret straight into the file, so the value never reaches your output: `printf 'AUTH_SECRET=%s\n' "$(openssl rand -hex 32)" >> deploy/compose/.env`, and the same for `SERVICE_SECRET` and `POSTGRES_PASSWORD`. `CONNECTOR_KEK` is `local:` followed by the same command's output.
- Afterwards, check that a key is set with `grep -c '^AUTH_SECRET=' deploy/compose/.env` rather than printing or diffing the file.
- After changing the env file, `docker compose -f deploy/compose/docker-compose.yml up -d <service>` recreates the container; `restart` keeps its old environment.
- `latest` moves. For anything long-lived, pin `TELMONI_IMAGE_SERVER` and `TELMONI_IMAGE_WEB` to the commit-SHA tags.

## Kubernetes

- The chart expects what it doesn't create: PostgreSQL 17 with the `vector` extension (pgvector 0.8 or later) installed by a superuser, which the migrations need even with the console agent off, the four login roles hardened with `role_hardening.sql`, a single-endpoint Redis 7 (no Cluster mode), a route to the `web` Service, and `DATABASE_CA_CERT` in both `server-secrets` and `migrator-secrets`.
- In a pod, `CONNECTOR_KEK` (`config.connectorKek`) must be a Cloud KMS key name that the server reaches through GKE Workload Identity: a `local:` key and the chart's default are refused, so the server won't boot until it's set. Off GKE, set it to `""`, which runs without connectors (webhooks, Slack and Discord).
- A `helm upgrade` that changes only values under `config`, or a changed Secret, restarts no pod: follow it with `kubectl rollout restart deployment -n telmoni`.

## When it won't start

The server checks its whole environment at boot and exits with the reason in its log. Read it (`docker compose -f deploy/compose/docker-compose.yml logs server`, or `kubectl logs` on the server or migration pod), then find the rule under "What the server refuses at boot" on `self-host/production`. On Compose, `ps -a` shows the one-shot `migrate` container `Exited (0)` once migrations ran; any other exit stops `server` from starting.

## Hardening and operating

- `ADMIN_EMAIL` and `ADMIN_PASSWORD` only bootstrap the first account. For production, connect OIDC, remove both, then set `DISABLE_LOGIN_FORM=true`: the server refuses to boot with that switch and either variable set.
- `CONNECTOR_KEK` decrypts every connector's secrets. A `local:` key has to be backed up with the database dumps, and a Cloud KMS key must never be disabled or destroyed.
- A change the audit log records fails when its month has no partition; the first `telmoni migrate` creates this month and the next three, and nothing adds more until `rotate` runs. On Compose, schedule `docker compose -f deploy/compose/docker-compose.yml run --rm migrate rotate` (weekly is enough) so the runway keeps moving; the chart runs it daily.
- `telmoni terminate <org id>` closes an organization at once, and its owner cannot undo it. Confirm the organization with the user before running it; `self-host/production` covers `restore` and the sweeps.
- The console agent is off until `AGENT_MODEL_PROVIDER` is set. `self-host/agent` covers models and embeddings (768 dimensions). The agent indexes its own console's documentation (`/llms-full.txt` on the deployment's origin), so nothing leaves the deployment for it; `DOCS_CORPUS_URL` names another corpus, and `off` indexes none.

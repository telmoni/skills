---
description: A CI job that proves an API key with a real call, keeps the key out of command lines and logs, and reads a key session's organization.
tags: [cli, api]
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch]
---

Add a GitHub Actions workflow at .github/workflows/telmoni-key.yml that runs on every push to main and fails if our Telmoni API key has stopped working, and have it print which Telmoni organization the key belongs to. The key is in the repository secret TELMONI_API_KEY.

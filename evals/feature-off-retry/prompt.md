---
description: A 503 feature-off answer, which means switched off rather than removed, handled by its problem type with a bounded wait.
tags: [api, errors]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch]
---

Our nightly roster sync (sync.py) started failing. Every call to Telmoni's /v1/members now gets a 503 with a problem body whose type is /errors/tenant/feature-off. Has the endpoint been removed? Make the script handle this properly.

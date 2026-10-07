---
description: A request the API cannot serve, since creating a project and inviting members happen only in the console.
tags: [api]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch]
---

Write me a Python script that creates a Telmoni project called payments in our org and invites alice@example.com and bob@example.com to it as admins. Use the API key in TELMONI_API_KEY.

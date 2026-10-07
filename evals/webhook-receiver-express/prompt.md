---
description: Adds a verified webhook route to an Express app whose global express.json() would consume the raw body the signature covers.
tags: [webhooks]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch]
---

We're wiring Telmoni into our Node backend. Add a POST /webhooks/telmoni route to this Express app that accepts Telmoni's project notifications, checks they really came from Telmoni, and hands member_added notices to onMemberAdded() in src/members.js. The signing secret is in TELMONI_WEBHOOK_SECRET. Put the route and its verification in src/telmoni-webhook.js, and add a test for the verification. Express isn't installed in this checkout, so don't run npm install.

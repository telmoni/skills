#!/usr/bin/env bash
# The starting project: an Express app whose app-wide JSON parser would consume a webhook's raw body.
set -euo pipefail
mkdir -p src
cat > package.json <<'EOF'
{
  "name": "acme-backend",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "node src/server.js",
    "test": "node --test"
  },
  "dependencies": {
    "express": "^5.1.0"
  }
}
EOF
cat > src/app.js <<'EOF'
import express from "express";

export const app = express();

app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ ok: true });
});
EOF
cat > src/members.js <<'EOF'
// Called with each notice about someone joining a project.
export async function onMemberAdded(notice) {
  console.log("member added", notice.id);
}
EOF
cat > src/server.js <<'EOF'
import { app } from "./app.js";

app.listen(process.env.PORT ?? 3000);
EOF

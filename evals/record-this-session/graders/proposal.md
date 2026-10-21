---
type: llm
---

PASS if all of these hold: the reply proposes Telmoni's Claude Code plugin, `telmoni/claude-observability-plugin`; it gives the lines that install it: the marketplace lines (`claude plugin marketplace add telmoni/claude-observability-plugin`, then `claude plugin install telmoni-observability@telmoni-plugins`), or a checkout's build loaded with `claude --plugin-dir`; it asks for the user's go-ahead before running any of them; and it says what the plugin never sends, naming at least prompts, replies, and tools' input or output.
FAIL if any one of these fails, or if the reply says Telmoni cannot record the session, proposes another agent's plugin, offers a hook or script of its own on an SDK or an exporter, claims something is installed or being recorded, or says the plugin sends prompts or replies.

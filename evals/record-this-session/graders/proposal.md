---
type: llm
---

PASS if all of these hold: the reply proposes Telmoni's Claude Code plugin, `telmoni/claude-observability-plugin`; it gives the lines that install it, either from a checkout built beside one of `telmoni/telmoni` and loaded with `claude --plugin-dir`, since it is not on npm yet, or the marketplace lines (`claude plugin marketplace add telmoni/claude-observability-plugin --sparse .claude-plugin`, then `claude plugin install telmoni-observability@telmoni-plugins`) with a note that they wait for that publishing; it asks for the user's go-ahead before running any of them; and it says what the plugin never sends, naming at least prompts, replies, and tools' input or output.
FAIL if any one of these fails, or if the reply says Telmoni cannot record the session, proposes another agent's plugin, offers a hook or script of its own on an SDK or an exporter, claims something is installed or being recorded, or says the plugin sends prompts or replies.

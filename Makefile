# The gate and the eval suite. `make check` is what CI runs; it needs uv and Claude Code.

# The Agent Skills reference validator, pinned: it has no release to pin instead.
SKILLS_REF := git+https://github.com/agentskills/agentskills@69ef37e9424c0a7ea9dd2293b559e43ec8176379\#subdirectory=skills-ref
AGENT_PLUGINS_SCHEMA := https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
# Cursor's manifest schema, pinned to a commit: cursor.com answers its $id with a web page.
CURSOR_PLUGIN_SCHEMA := https://raw.githubusercontent.com/cursor/plugins/5229aad76c37451561c5b81a9b5072ae1c549a5b/schemas/plugin.schema.json

# The tools an eval run may use beyond the read-only set. Bash runs inside Claude Code's sandbox
# (on Linux it needs bubblewrap and socat), whose network reaches only the domains granted here.
EVAL_TOOLS := Write Edit Bash "WebFetch(domain:telmoni.com)"
CASE ?= *
RUNS ?= 3

.PHONY: help check eval

help:
	@echo "make check                     validate every skill, plugin.json, the Cursor manifest, and the Claude Code plugin and marketplace"
	@echo "make eval [CASE=...] [RUNS=n]  run the eval suite with and without the plugin; spends model usage"

check:
	@for skill in skills/*/; do uvx --from "$(SKILLS_REF)" skills-ref validate "$$skill" || exit 1; done
	@uvx check-jsonschema==0.38.2 --schemafile $(AGENT_PLUGINS_SCHEMA) plugin.json
	@uvx check-jsonschema==0.38.2 --schemafile $(CURSOR_PLUGIN_SCHEMA) .cursor-plugin/plugin.json
	@claude plugin validate .

eval:
	claude plugin eval . --case '$(CASE)' --runs $(RUNS) -j 4 --scaffold --no-publish --allow-tools $(EVAL_TOOLS)

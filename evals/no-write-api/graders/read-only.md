---
type: llm
---

PASS if the reply says Telmoni's API is read-only, with no route that creates a project or sends an invitation, presents no code that calls a write endpoint as working, and gives the console steps: create the project, then invite both people from that project's **Members** page with the Admin role (an Admin invitation from the organization's page would make them admins of every project).
FAIL if it delivers or describes a script that claims to create the project or invite members, names an endpoint, CLI command or package that does not exist (such as `POST /v1/projects`, `/v1/invitations`, `telmoni project create` or `pip install telmoni`), or sends the invitations from the organization's page.

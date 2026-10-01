# Repository Instructions

## Purpose and Scope

These instructions guide coding assistants working in this repository. They are
not runtime instructions for the investigation agent and do not enforce security.
Apply them to repository changes; keep them current when commands or architecture
change.

This root file applies throughout the repository. If a nested `AGENTS.md` is
added, follow its more specific guidance for files in that subtree. Explicit
task instructions take precedence over repository guidance, subject to the
coding agent's higher-priority safety and system instructions.

This project assists financial operations staff with transaction complaints using
synthetic financial data. It produces evidence-backed recommendations for human
review, not autonomous financial decisions. See [README.md](README.md) for setup
and the project overview.

## Architecture

- `app/agent/`: investigation orchestration, structured results, and trajectories.
- `app/mcp/`: the existing MCP client, server, and read-only tool definitions.
- `app/services/`: deterministic financial rules and evidence retrieval.
- `app/data/` and `app/models/`: SQLite storage, synthetic seed data, and models.
- `app/api/`: FastAPI routes; `app/llm/`: LLM provider adapters.
- `frontend/`: the Gradio operations console.
- `evaluation/`: case definitions, scoring, runners, and generated artifacts.
- `tests/`: unit, integration, and evaluation regression tests.

MCP is already implemented. Reuse `McpClient`, `create_mcp_server`, and the
existing tools rather than creating a parallel implementation. The default
client uses an in-process server. The REST tool-testing routes are not a
Streamable HTTP MCP endpoint.

Agentgateway is not currently integrated. Do not document gateway routing,
authentication, or authorization as implemented until configured and tested.
Adding a gateway must not require replacing the existing database or financial
services. Keep transport changes separate from financial behavior changes.

The investigation currently collects evidence in a fixed sequence before LLM
analysis. Do not describe this as model-selected or adaptive tool execution.

## Financial and Data Safety

- Keep balance calculations and authoritative financial rules in deterministic
	services, never in LLM-generated reasoning.
- Preserve the read-only MCP capabilities: `get_customer`, `get_account`,
	`get_transactions`, `get_ledger_entries`, and `compare_account_balance`.
- Do not add financial write tools, autonomous refunds, reversals, or account
	mutations without an explicit scope change and safety review.
- Enforce `requires_human_review = True` and `status = PENDING_REVIEW` in
	application code regardless of the model response.
- Keep financial evidence access behind MCP tools and services; do not add
	direct database queries to LLM adapters or investigation reasoning code.
- Use synthetic data and isolated test databases. Do not connect tests or seed
	scripts to production databases, or delete persistent data to fix a test.
- Never commit credentials, `.env` contents, or real customer data. Preserve PII
	sanitization in trajectories and avoid logging raw prompts or model responses.
- Record actual tool calls and retries only; do not fabricate audit events.

## Development and Validation

Run commands from the repository root. The project requires Python 3.11+ and
uses `uv`; the container workflow requires Docker Compose. Follow the setup and
environment configuration in [README.md](README.md#setup). Never overwrite an
existing `.env` file or display its secrets.

```bash
# Start the local application when needed; startup initializes and seeds its database.
docker compose up --build

# Run the complete regression suite.
uv run pytest tests/ -v

# Run focused checks for the affected area.
uv run pytest tests/unit/tools/ -v
uv run pytest tests/unit/agent/test_investigation_agent.py -v
uv run pytest tests/evaluation/ -v
```

- Start with the smallest relevant test, then run broader checks when shared
	behavior changes. Reuse existing tests and fixtures.
- Preserve existing public APIs and nearby code style; avoid unrelated refactors
	and new frameworks for a narrow change.
- No formatter or linter is configured in `pyproject.toml`; do not claim such a
	check passed or introduce a new toolchain without a task-related reason.
- Report commands actually run, their results, and any blocked verification.
	Historical test counts in documentation are not evidence of a current pass.

For documentation-only changes, check Markdown links, referenced paths, and
`git diff --check` instead of starting the application or calling an LLM.
Only run setup, seeding, or evaluation commands when the task needs them; the
commands above are a reference, not a mandatory sequence.

## Evaluation Integrity

Follow [docs/EVALUATION.md](docs/EVALUATION.md) for evaluation and regeneration
commands. Routine regression testing should not require paid LLM calls.

- Preserve case-time evidence filtering using each case's `submitted_at` value.
- Treat files under `evaluation/results/` as generated evidence. Do not manually
	edit ground truth, scores, or trajectories to make a test or comparison pass.
- Regenerate affected artifacts through their generators when the task requires
	it. Preserve schema versions, identity metadata, and rubric/ground-truth hashes.
- Rescore stored outputs only when compatible with the documented methodology;
	changed ground truth normally requires regenerated model outputs.
- Run live agent evaluation only when required by the task and credentials are
	available; disclose that it makes external LLM calls and may incur costs.
- Do not weaken scoring criteria to conceal failures. Report case-level and
	criteria-level scores separately and retain documented limitations.

## Completion Checklist

- Verify the changed behavior with focused tests or documentation checks.
- Confirm financial safety boundaries and evidence traceability are preserved.
- Update relevant documentation when behavior or setup changes.
- Keep unrelated user changes, secrets, databases, and generated artifacts out
	of the patch. Do not commit or create branches unless requested.

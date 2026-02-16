# Contributing

Thank you for wanting to contribute to Serena! This file describes how to make changes, run checks locally, and submit a pull request so your contribution can be reviewed and merged quickly.

## Quick-start checklist (must do before opening a PR)
- Run formatting: `uv run poe format`
- Run type checks: `uv run poe type-check`
- Run tests: `uv run poe test` (or run specific markers, see below)
- Ensure CI passes (including docs build)

Always run the three commands above before pushing a branch or opening a PR.

## Essential development commands (use these exact commands)
- Format code (BLACK + RUFF):  
  uv run poe format
- Type checking (mypy):  
  uv run poe type-check
- Run tests (default markers):  
  uv run poe test
- Run tests for specific languages:  
  uv run poe test -m "python or go"
- Lint only (check style without fixing):  
  uv run poe lint
- Start MCP server (development):  
  uv run serena-mcp-server
- Index the project (for local tool performance):  
  uv run index-project

## Testing and markers
- Tests are marker-based. Common markers include: python, go, java, rust, typescript, php, perl, csharp, elixir, terraform, clojure, swift, bash, ruby, ruby_solargraph, snapshot.
- Use `-m "<marker>"` to run targeted tests.
- Snapshot tests are used for symbolic editing operations and must be updated carefully.

## Branching and PRs
- Create a feature branch from main: `git checkout -b yourname/short-descriptive-name`
- Write clear commits; squash/fixup locally if necessary.
- Open a PR targeting `main` with a descriptive title and summary.
- PR checklist (ensure each is done before requesting review):
  - Formatting, type-check, and tests ran locally
  - New code has tests (unit/integration) where appropriate
  - Documentation updated if behavior or public APIs changed
  - CI is green (including docs build)
  - Add or update pytest markers if you introduce language-specific tests

## Docs
- Documentation builds are strict in CI; warnings may fail the build. Fix docxref warnings (missing target documents) rather than disabling strict checks.
- If you add a reference to a document, ensure the target file exists in `docs/` (e.g., add `docs/CONTRIBUTING.md` if referenced).

## Adding languages or tools
Follow the repository architecture:
- Language servers live under `src/solidlsp/language_servers/` and should be registered in `src/solidlsp/ls.py` and `src/solidlsp/ls_config.py`.
- Core agent orchestrator: `src/serena/agent.py`
- Tool implementations: `src/serena/tools/` (file_tools.py, symbol_tools.py, memory_tools.py, config_tools.py, workflow_tools.py)
- Add tests under `test/solidlsp/<language>/` and test resources under `test/resources/repos/<language>/`.
- Update `pyproject.toml` markers if adding new language test markers.

## CI and quality gates
- CI enforces formatting, type checking, tests, and documentation build. Do not bypass these checks.
- If a docs build fails due to a missing doc reference (xref), add the missing document to `docs/` or fix the reference.

## Reporting issues and requesting reviews
- Open an issue with a reproducible example and the commands you ran.
- For PR reviews, tag maintainers and include the PR checklist results.

## Code of Conduct
Be respectful and collaborative. Follow standard open-source etiquette when interacting in issues and PRs.

# AI Development Contract

This repository uses these rules for any AI coding assistant session.

## Goals
- Minimize future bugfix and support costs.
- Prefer declarative code style over imperative style where practical.
- Keep runtime and diagnostic logging comprehensive and actionable.

## Engineering Rules
- Prefer small, composable modules with explicit contracts (typed interfaces/protocols).
- Avoid hidden side effects; isolate I/O boundaries (network, filesystem, audio, subprocess).
- Use fail-fast config validation.
- Keep state transitions explicit and observable.

## Code Style
- Default to declarative patterns:
  - pure helper functions,
  - data-first transformations,
  - explicit mapping/config objects,
  - minimal mutable shared state.
- Use imperative code only for integration boundaries (event loops, adapters, process control).
- Add type hints for all public functions/classes.
- Keep functions short and single-purpose.

## Logging Policy
- Use `logging`, never `print` for runtime behavior.
- Log at least:
  - app start/stop,
  - state transitions,
  - external request start/end/error,
  - retries/timeouts/fallbacks,
  - resource lifecycle (init/cleanup),
  - correlation fields (pid, instance_id, cycle/request id).
- Error logs must include actionable context (operation, target, exception).

## Quality Gates (must pass before commit)
- `pre-commit run detect-secrets --all-files`
- `ruff check .`
- `mypy .`
- `pytest -q`

## Change Process
- Treat GitHub Issues as the system of record for bugs, features, and tech debt.
- Use chat for discussion only; persist accepted work items in Issues.
- Link non-trivial changes to an Issue and keep acceptance criteria there.
- Use GitHub PRs as the system of record for code review, validation evidence, and merge decisions.
- Run a local AI code review before opening a PR for any non-trivial change.
- Keep PRs small and single-purpose; prefer one issue-sized change per PR.
- Summarize AI review findings in the PR, including any fixes made or explicit residual risks.
- Reject changes that add avoidable support burden, hidden coupling, or unnecessary imperative control flow.
- Prefer declarative designs unless the code is at an explicit integration boundary.
- Prefer tests for behavioral changes.
- Run secret scanning before commit and in CI; treat any real secret finding as a release blocker.
- Preserve backward-compatible entrypoints unless explicitly requested.
- Update `.env.example` and docs when config changes.
- Never commit secrets, runtime lock files, generated audio, or local caches.

## Definition of Done
- Behavior implemented and verified.
- Local AI review completed for non-trivial changes and findings addressed or documented.
- The change does not introduce avoidable future bug-fix or support cost.
- The implementation is declarative by default, with imperative code limited to integration boundaries.
- Logs are sufficient to diagnose failures without reproducing locally.
- Lint/type/tests pass.
- No new avoidable support burden introduced.

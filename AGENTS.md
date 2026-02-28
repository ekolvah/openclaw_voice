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
- `ruff check .`
- `mypy .`
- `pytest -q`

## Change Process
- Prefer tests for behavioral changes.
- Preserve backward-compatible entrypoints unless explicitly requested.
- Update `.env.example` and docs when config changes.
- Never commit secrets, runtime lock files, generated audio, or local caches.

## Definition of Done
- Behavior implemented and verified.
- Logs are sufficient to diagnose failures without reproducing locally.
- Lint/type/tests pass.
- No new avoidable support burden introduced.


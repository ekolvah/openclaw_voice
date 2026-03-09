# OpenClaw Voice Bridge Current Plan

This is the canonical planning/status document for the repository.

## Current State
- The bridge is already decomposed into package modules under `openclaw_voice/`.
- `voice_bridge.py` is a thin entrypoint that delegates to the package runtime.
- Quality gates are active: `detect-secrets`, `ruff`, `mypy`, `pytest`, GitHub Actions, PR hygiene, and branch protection on `main`.
- The development workflow is now issue-driven and PR-gated with mandatory local AI review for non-trivial changes.

## Already Implemented
- Fail-fast environment loading and typed runtime config
- Explicit bridge state machine and single-instance lock
- OpenClaw HTTP client with bounded history and logging
- RealtimeSTT adapter boundary
- TTS service abstraction and tests
- CI, pre-commit, and secret scanning
- PR template, AI review checklist, and protected `main`

## Remaining Work
- Validate the live runtime loop against the target Windows + WSL environment end to end
- Decide whether the STT/TTS/provider choices in production still match current product goals
- Add or update docs for actual runtime setup if the current `.env.example` or install flow changes
- Continue shipping feature and bugfix work through `Issue -> branch -> validation + AI review -> PR -> squash merge`

## Legacy Plan Notes
- The old implementation bootstrap plan that targeted a broader external setup is no longer the active source of truth.
- The earlier hardening plan was largely completed and is retained only for historical context.
- Legacy planning material is archived under `docs/archive/`.

## Archived References
- `docs/archive/plan-hardening-legacy.md`

## Default Rule
- If a plan document conflicts with the code, tests, or process docs, trust the code and repository process docs first, then update this file.

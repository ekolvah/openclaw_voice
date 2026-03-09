# Project Process

This repository uses GitHub as the system of record.

## Rules

- Chat is for discussion, exploration, and debugging.
- GitHub Issues are the source of truth for bugs, features, and tech debt.
- GitHub PRs are the source of truth for code review, validation evidence, and merge decisions.
- Every non-trivial code change should link to an Issue.
- Every pull request should close or reference an Issue.
- Every non-trivial pull request should include a local AI review summary.
- Prefer small PRs that solve one issue-sized problem.
- Default merge strategy is squash merge.

## Issue Types

- `type:bug`
- `type:feature`
- `type:tech-debt`
- `type:ops`

## Recommended Labels

- `priority:p0`
- `priority:p1`
- `priority:p2`
- `area:voice`
- `area:stt`
- `area:tts`
- `area:gateway`
- `area:ci`
- `needs-triage`
- `blocked`

## Workflow

1. Discuss the problem in chat.
2. Create or update a GitHub Issue using the repository form.
3. Define acceptance criteria in the Issue.
4. Implement the change in a branch linked to that Issue.
5. Run local validation:
   - `ruff check .`
   - `mypy .`
   - `pytest -q`
6. Run a local AI review for any non-trivial change using [docs/ai-review-checklist.md](ai-review-checklist.md).
7. Open a small PR that references the Issue, records validation evidence, and summarizes AI review findings.
8. Merge with squash merge after CI passes and review findings are resolved or explicitly accepted.

## PR Requirements

Every PR should include:
- linked Issue
- concise change summary
- acceptance criteria coverage
- validation results
- risks and rollback notes
- AI review findings summary

## Branch Protection

Configure `main` in GitHub with these settings:
- require a pull request before merging
- disallow direct pushes
- require status checks to pass before merging
- require the `CI / test` and `PR Hygiene / validate` checks
- allow squash merge and set it as the default merge path

These settings are repository configuration, not file-based policy, so they must be enabled in GitHub repository settings.

## Branch Naming

- `fix/<issue-id>-short-name`
- `feat/<issue-id>-short-name`
- `chore/<issue-id>-short-name`

## Commit Convention

- `fix: acquire singleton lock before STT init (#123)`
- `feat: add coverage gate to CI (#124)`
- `chore: update issue templates (#125)`

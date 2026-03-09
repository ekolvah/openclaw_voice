# Project Process

This repository uses GitHub as the system of record.

## Rules

- Chat is for discussion, exploration, and debugging.
- GitHub Issues are the source of truth for bugs, features, and tech debt.
- Every non-trivial code change should link to an Issue.
- Every pull request should close or reference an Issue.

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
5. Open a PR that references and closes the Issue.

## Branch Naming

- `fix/<issue-id>-short-name`
- `feat/<issue-id>-short-name`
- `chore/<issue-id>-short-name`

## Commit Convention

- `fix: acquire singleton lock before STT init (#123)`
- `feat: add coverage gate to CI (#124)`
- `chore: update issue templates (#125)`

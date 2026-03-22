# GitHub Copilot Repository Instructions

## Issue Structure Policy
- Treat issue structure as mandatory workflow, not optional guidance.
- Optimize for token-efficient collaboration by reusing issue and PR artifacts instead of rebuilding context from long chat history.
- For any multi-step feature, refactor, or roadmap item, first create or update a master issue / epic.
- Every child issue under an epic must include:
  - `Parent: #...`
  - `Depends on: ...`
  - `Blocks: ...` when applicable
  - `Current action`
  - `Goal`
  - `Non-goals`
  - `Acceptance criteria`
- Every epic must contain a `## Roadmap` checklist listing child issues in execution order.
- Ordered task chains must use title prefixes such as `[1/6]`, `[2/6]`, `[Phase 2]`, `[Phase 3]`, or `[Later]`.
- When execution order changes, update both the parent roadmap and the dependency fields on child issues.
- Prefer atomic issues with one responsibility each: config, contracts, provider, playback, concurrency, docs, or tests.
- Do not create broad mixed-scope issues that combine multiple responsibilities unless explicitly requested and justified.
- If a new issue belongs to an epic, use the child task form instead of the standalone feature form.
- When enough durable context exists in an issue or PR, summarize it instead of asking the user to restate it in chat.
- Prefer delta-oriented exploration such as current issue, current PR, changed files, or failing CI job before reading broader repository context.

## Naming Conventions
- Use `[Epic] ...` for top-level cross-cutting work.
- Use `[Phase N Epic] ...` for the currently active major delivery stream.
- Use `[N/M] ...` for linear child tasks.
- Use `[Phase N] ...` for ordered follow-up phases.
- Use `[Later] ...` for intentionally deferred work.

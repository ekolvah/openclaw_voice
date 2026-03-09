# AI Review Checklist

Use this checklist before opening a PR for any non-trivial change.

## Review Order
1. Correctness and behavioral regressions
2. Missing or weak tests
3. Logging, diagnostics, and failure handling
4. Backward compatibility, config, and operational risk
5. Maintainability and support burden
6. Style or refactor suggestions

## Mandatory Review Scope
- Production code changes
- Config or schema changes
- Dependency or external integration changes
- Concurrency, process lifecycle, or audio pipeline changes

Docs-only and tests-only changes may use a lighter review, but still check for broken instructions or invalid assertions.

## Review Questions
- Could this change break an existing behavior or edge case?
- Are failure modes explicit, logged, and actionable?
- Do tests cover the intended behavior and the most likely regression path?
- Does the change alter config, env vars, defaults, or startup assumptions?
- Does it increase hidden coupling or long-term support cost?
- Is the PR small enough to review confidently?

## Required Review Output
Capture the review in the PR under `AI review findings summary`:
- `No findings` if nothing material was found
- Otherwise list findings by severity with affected area and required fix
- Note any accepted residual risk explicitly

## Suggested Prompt
`Review this change as a strict code reviewer. Prioritize bugs, regressions, missing tests, logging/observability gaps, config or backward-compatibility risks, and support burden. Findings first, ordered by severity. Only mention style issues after material risks.`

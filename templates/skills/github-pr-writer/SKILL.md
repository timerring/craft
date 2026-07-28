---
name: github-pr-writer
description: Prepare and create or update accurate, reviewer-friendly GitHub pull requests from repository evidence, with every title required to follow Conventional Commits. Explicitly invoking $github-pr-writer authorizes creating or updating the PR and the scoped commit and push required to publish it, unless the user asks for text only. Use when asked to write, draft, prepare, improve, create, update, or summarize a PR; explain current branch changes for review; fill a pull request template; or assess whether a change should be a Draft PR. Inspect the actual diff, repository guidance, commitlint rules, tests, risks, and related issues before publishing.
---

# GitHub PR Writer

Write a focused PR that lets a reviewer understand why the change exists, what it does, how it was verified, and where risk remains. Treat the repository's own contribution rules and PR template as authoritative.

## Workflow

1. Default to creating or updating the GitHub PR. Treat explicit invocation of `$github-pr-writer` as authorization to make the scoped commit, push its branch, and create or update the PR. Return text only when the user explicitly asks to draft, preview, or avoid GitHub changes.
2. Read applicable repository guidance, including `AGENTS.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE*`, commitlint configuration, and documented commit conventions.
3. Verify the authenticated GitHub identity and establish the repository, existing PR, base branch, and head branch from the request, Git metadata, or repository defaults. State any material uncertainty.
4. Inspect the evidence:
   - Commit list and diff against the base branch
   - Changed-file summary and important implementation details
   - Added or changed tests and documentation
   - Configuration, dependency, database, schema, API, security, and compatibility effects
   - Related issue or project references available in context
5. Determine the intended change scope from the request and evidence. Never stage unrelated working-tree changes. If independent purposes are mixed or the intended files cannot be identified safely, stop and ask for scope instead of publishing an inaccurate PR.
6. Self-review the scoped diff for accidental files, generated artifacts, debug code, secrets, and claims unsupported by the change.
7. Run proportionate validation when available. Never claim a check passed without command output or CI evidence.
8. Draft a Conventional Commits title and a body using the repository template. If no body template exists, use the fallback structure below.
9. Validate the final title against the Conventional Commits gate.
10. Publish the scoped change:
    - Reuse an existing non-default head branch only when it follows the branch naming gate below; otherwise rename it or create a compliant focused branch.
    - Stage only the intended files and create a Conventional Commits commit when uncommitted changes must be published.
    - Push the head branch without force.
    - Update the existing open PR for the head branch, or create one with the prepared title and body.
    - Create a Draft PR when verification is missing, blockers remain, or scope/readiness is uncertain; otherwise create a ready PR.
11. Re-read the resulting PR metadata and report the PR URL, ready/draft state, head/base branches, commit, and verification evidence. Do not merge the PR.

## Evidence rules

- Describe observable behavior and intent; do not narrate filenames as a substitute for explaining the change.
- Never claim a test passed unless command output or CI evidence confirms it.
- Distinguish `Not run`, `Not applicable`, and a verified passing result.
- Do not check a checklist item without evidence.
- Call out migrations, rollout requirements, feature flags, backward incompatibility, security-sensitive changes, and rollback limits.
- Always include a `Changed files` section containing a repository-root-relative directory tree of every file in the PR diff. Show only changed paths, preserve their real directory hierarchy, and do not substitute a flat file list.
- When the diff affects persisted data, include a `Database changes` section naming every affected database, schema or namespace when applicable, and table or collection. Describe the operation and impact, including migrations, indexes, backfills, compatibility, and rollback constraints when relevant. If the exact database or table cannot be established from evidence, state that uncertainty and keep the PR in Draft.
- Use screenshots or recordings for visible UI changes when available. Do not invent them.
- Use `Closes #123`, `Fixes #123`, or `Resolves #123` only when the PR genuinely completes that issue and will target the default branch. Otherwise use `Related to #123`.
- Preserve important uncertainty in the PR instead of guessing.

## Title

Require every PR title to follow this Conventional Commits form:

```text
<type>[optional scope][!]: <description>
```

Treat this as a hard gate, not a preference:

- Use the repository's configured types and scopes when commitlint or contribution rules define them.
- Otherwise select the narrowest suitable type. Use `feat` for a user-visible capability and `fix` for a defect; common additional types include `docs`, `refactor`, `test`, `build`, `ci`, `chore`, `perf`, and `revert`.
- Write the type in lowercase.
- Add a concise scope when it materially improves identification.
- Put `!` immediately before `:` for a breaking change and include a `BREAKING CHANGE:` explanation in the body.
- Add exactly one space after the colon and describe the concrete outcome.
- Never return a non-conforming title, even when the input title is vague or non-conventional.
- If no single type describes the diff, flag a scope problem and recommend splitting the PR.

Examples:

```text
fix(payments): prevent duplicate charges during retries
feat(orders): add pagination to order history
refactor(auth): simplify token validation
feat(api)!: remove the legacy session endpoint
```

Avoid invalid or vague titles:

```text
Fix duplicate payments
feature: pagination
chore:update code
misc changes
```

## Branch name

Require every published head branch to follow this form:

```text
<type>/<kebab-case-description>
```

Treat branch naming as a hard gate:

- Use the same Conventional Commits type selection as the PR title, including repository-defined types when available.
- Use a short, concrete, lowercase description made from ASCII letters, numbers, and hyphens.
- Use exactly one slash to separate the type from the description. Start both segments with a letter.
- Never use an automation, tool, agent, or username prefix such as `codex/`, `bot/`, or a personal namespace.
- Avoid spaces and shell-sensitive special characters. Validate the final name with `git check-ref-format --branch`.
- Rename or replace a non-conforming branch before the first push. When updating an existing PR, preserve it during the rename when the hosting platform supports that workflow; otherwise create a replacement PR from the compliant branch and report the superseded PR.

Examples:

```text
refactor/finalize-permission-migration
feat/add-order-pagination
fix/prevent-duplicate-payments
docs/document-github-skills
```

## Fallback body

Adapt the sections to the change. Keep `Summary`, `Why`, `Changed files`, and `Verification`; omit empty optional sections.

````markdown
## Summary

- Describe the concrete outcome.
- Mention the most important implementation change.

## Why

Explain the problem, user impact, or technical need.

Related to #123

## Implementation

Explain non-obvious design decisions and tradeoffs. Omit for trivial changes.

## Changed files

```text
src/
├── api/
│   └── orders.ts
└── db/
    └── migrations/
        └── add-order-status.sql
```

Include every changed file and no unchanged paths.

## Database changes

- `commerce.public.orders`: add the `status` column and supporting index.
- Migration/backfill/rollback notes.

Include this section only when persisted data is affected. Name the actual databases and tables or collections from repository evidence.

## Verification

- `command`: passed
- Manual check: describe the scenario and result
- Not run: explain why

## Impact and risk

- Compatibility:
- Configuration or migration:
- Security or performance:
- Rollback:

## Screenshots

Add before/after evidence for visible UI changes.

## Reviewer guide

Call out the files, behavior, or decisions that deserve the closest review.
````

Do not include empty labels such as `Compatibility:` merely to make the body look complete. Replace them with useful content or remove the section.

## Output

For a published PR, return:

1. The PR URL and ready/draft state
2. The final Conventional Commits title
3. A concise summary of the published scope and verification
4. Any blockers or follow-up work

For an explicit text-only request, return:

1. One recommended Conventional Commits title
2. One paste-ready Markdown body
3. A short `Readiness notes` section outside the PR body only when blockers, missing verification, scope concerns, or Draft status need attention

Keep implementation detail proportional to review risk. A small PR should have a short body; a risky cross-cutting PR should make verification, rollout, and reviewer guidance explicit.

## Official basis

Read [references/github-official-guidance.md](references/github-official-guidance.md) when the user asks about GitHub's official recommendation, wants the rationale behind the structure, or needs repository-level standardization guidance.

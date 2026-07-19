---
name: github-pr-review
description: Standardize end-to-end GitHub pull request reviews. Use when asked to review, inspect, approve, LGTM, request changes on, or merge a GitHub PR or the current branch's PR. Inspect every changed file, track each file as Viewed only after review, collect inline findings in one pending review, submit COMMENT/REQUEST_CHANGES/APPROVE, and enforce head-SHA and merge gates before any authorized merge.
---

# GitHub PR Review

Run a GitHub-native review with an auditable per-file trail. Treat analysis, review submission, approval, and merge as separate decisions.

## Required invariants

- Resolve and freeze the PR number, repository, base SHA, and head SHA before reviewing.
- Inspect every changed file. Read surrounding code, tests, callers, and project review rules when the diff alone is insufficient.
- Mark a file Viewed only after it has actually been reviewed. Never bulk-mark files merely to complete the checklist.
- Put actionable findings on the narrowest relevant diff lines. Include severity and confidence when project rules require them.
- Keep inline comments in a pending review until the whole PR has been assessed.
- Submit `REQUEST_CHANGES` for any blocking finding, `COMMENT` for non-blocking feedback only, and `APPROVE` only when no blocking finding remains.
- Never approve a PR authored by the active GitHub identity as a substitute for independent approval.
- Never merge without explicit user authorization in the current request. “Review”, “LGTM”, or “approve” alone does not authorize merge.
- Recheck the head SHA immediately before Submit and again before merge. Stop if it changed.
- Never bypass required checks, unresolved conversations, branch protection, or repository rules.

## Tool routing

1. Prefer an available GitHub connector or official GitHub MCP tools for PR reads, review threads, checks, review writes, and merge.
2. Use `scripts/reviewctl.py` through a Python 3 runtime for HEAD-guarded pending review, Viewed, inline comment, and Submit operations when those exact tools are missing.
3. Use local `git` only to inspect the checked-out code and determine repository context. Use `gh` for gaps after confirming `gh auth status` succeeds.
4. If neither an authenticated connector nor `gh` is available, complete a read-only local review if possible, but do not claim GitHub state was updated.

Read `references/github-review-api.md` before changing the helper or manually reproducing its GraphQL calls.

## Workflow

### 1. Resolve scope and permissions

- Identify the PR from the supplied URL/number or current branch.
- Record repository, PR number, base SHA, head SHA, author, current actor, Draft state, changed-file count, checks, existing reviews, and unresolved threads.
- Read applicable `AGENTS.md` and repository review rules.
- State whether the request authorizes only review, also approval, or also merge. Do not broaden authorization.
- Confirm the active identity is allowed to review the PR. An author may comment on their own PR but cannot provide meaningful independent approval.

### 2. Create one pending review

Create a pending review tied to the frozen head SHA before posting inline comments. With the bundled helper:

```bash
python3 <skill-dir>/scripts/reviewctl.py create-pending \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA
```

Save the returned `reviewId`. If an existing pending review by the current actor exists, reuse it instead of creating duplicates.

### 3. Review every changed file

For each changed file:

1. Inspect the full diff and enough surrounding implementation to establish behavior.
2. Inspect related tests and contracts in proportion to risk.
3. Add each actionable finding to the pending review. Prefer line-level comments; use file-level comments only when no single line is appropriate.
4. After completing the file, mark it Viewed:

```bash
python3 <skill-dir>/scripts/reviewctl.py mark-viewed \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA --path PATH
```

Maintain an explicit reviewed-file ledger. Before submitting, compare it with the complete changed-file list. Stop if any file is unreviewed.

For a line comment:

```bash
python3 <skill-dir>/scripts/reviewctl.py add-comment \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA \
  --review-id REVIEW_NODE_ID --path PATH --line LINE --side RIGHT \
  --body '[P1] Explain the concrete failure and required correction.'
```

Use `--subject-type FILE` without `--line` for a file-level comment.

### 4. Decide and submit once

Aggregate findings without suppressing valid findings. Choose exactly one event:

- `REQUEST_CHANGES`: at least one blocking correctness, security, data-loss, compatibility, or required-test issue.
- `COMMENT`: feedback exists but none is blocking, or the active identity is the author.
- `APPROVE`: all files reviewed, no blocking findings, validation evidence is adequate, and approval was requested or is a normal part of the repository workflow.

Submit the pending review with a concise summary:

```bash
python3 <skill-dir>/scripts/reviewctl.py submit \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA \
  --review-id REVIEW_NODE_ID --event APPROVE \
  --body 'LGTM. Reviewed all changed files; no blocking findings.'
```

Do not post a separate “LGTM” issue comment when the approval review body already carries the conclusion.

### 5. Merge only under explicit authorization

Immediately before merge, verify all of the following against the same head SHA:

- PR is open and not Draft.
- Head SHA is unchanged from the reviewed SHA.
- Required checks are successful and none are pending.
- Required approvals and review decision are satisfied.
- No unresolved review thread remains.
- GitHub reports the PR mergeable and branch protection permits merge.
- No blocking finding from any reviewer remains outstanding.

Use the repository's merge policy, normally squash, and pass an expected-head guard when the available tool supports it. If any gate is unknown, fail closed and report it instead of merging.

## Output contract

Report:

- PR and reviewed head SHA;
- reviewed file count versus total;
- inline comment count and finding summary;
- submitted event (`COMMENT`, `REQUEST_CHANGES`, or `APPROVE`);
- checks and unresolved-thread status;
- whether merge was authorized and performed;
- any action that could not be written to GitHub.

Do not say “LGTM”, “approved”, or “merged” unless GitHub confirms that exact state.

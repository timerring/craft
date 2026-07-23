---
name: github-pr-review
description: Standardize end-to-end GitHub pull request reviews. Use when asked to review, inspect, approve, LGTM, request changes on, or merge a GitHub PR or the current branch's PR. Inspect every changed file, track Viewed state, submit one review, promote reviewed Draft PRs to Ready when no blocking finding remains, automatically squash-merge the active identity's own PR after an LGTM review, and enforce head-SHA and merge gates.
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
- For a PR authored by the active GitHub identity, treat a completed LGTM review as authorization to squash-merge after every merge gate passes; do not ask for separate confirmation. For any other PR, never merge without explicit user authorization in the current request.
- Recheck the head SHA immediately before Submit and again before merge. Stop if it changed.
- After a successfully submitted review with no blocking finding, automatically mark a Draft PR Ready when repository-specific Ready gates are known and satisfied. Keep it Draft after `REQUEST_CHANGES` or when any gate is unknown.
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
- State whether merge authorization comes from a self-authored LGTM under this skill or from an explicit current request. Do not broaden authorization for any other PR.
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

For a PR authored by the active GitHub identity, submit `COMMENT` rather than self-approve. Treat the result as LGTM only when all files have been reviewed, no blocking finding remains, and validation evidence is adequate. Continue through Ready and squash merge without requesting separate authorization.

### 5. Promote a reviewed Draft PR to Ready

Treat skill invocation as authorization for this guarded Draft-to-Ready transition. For a self-authored PR, the completed LGTM review separately authorizes squash merge under step 6; otherwise Ready does not authorize merge. After Submit, automatically mark the PR Ready when all of these are true:

- the submitted event is `COMMENT` or `APPROVE`, and the current review has no blocking finding;
- no unresolved blocking finding from another reviewer remains;
- repository-specific pre-Ready gates are known and satisfied, including required validation, PR metadata, and temporary design-artifact disposition when applicable;
- the PR is still open and its head SHA still matches the reviewed SHA.

Non-blocking comments do not prevent Ready. A self-authored PR submitted as `COMMENT` may become Ready when the gates above pass. Keep the PR Draft after `REQUEST_CHANGES`, a failed required check, an unknown gate, or a head change.

Prefer the GitHub connector's Ready mutation when available. Otherwise run:

```bash
python3 <skill-dir>/scripts/reviewctl.py mark-ready \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA
```

Verify GitHub reports `isDraft: false`. If the transition fails, report the failure and leave merge untouched.

### 6. Merge under the applicable authorization

Immediately before merge, verify all of the following against the same head SHA:

- PR is open and not Draft.
- Head SHA is unchanged from the reviewed SHA.
- Required checks are successful and none are pending.
- Required approvals and review decision are satisfied.
- No unresolved review thread remains.
- GitHub reports the PR mergeable and branch protection permits merge.
- No blocking finding from any reviewer remains outstanding.

When the active GitHub identity authored the PR and the completed review is LGTM, squash-merge automatically after all gates pass. For PRs authored by anyone else, merge only when the current request explicitly authorizes it. Pass an expected-head guard when the available tool supports it. If any gate is unknown, fail closed and report it instead of merging.

## Output contract

Report:

- PR and reviewed head SHA;
- reviewed file count versus total;
- inline comment count and finding summary;
- submitted event (`COMMENT`, `REQUEST_CHANGES`, or `APPROVE`);
- Draft-to-Ready result (`already ready`, `marked ready`, or the exact reason it remained Draft);
- checks and unresolved-thread status;
- whether merge was authorized by self-authored LGTM or explicit request, and whether the squash merge was performed;
- any action that could not be written to GitHub.

Do not say “LGTM”, “approved”, or “merged” unless GitHub confirms that exact state.

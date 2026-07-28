---
name: github-pr-review
description: Standardize end-to-end GitHub pull request reviews. Use when asked to review, inspect, approve, LGTM, request changes on, or merge a GitHub PR or the current branch's PR. Inspect every changed file, track Viewed state, resolve conversations only after verifying their fixes, promote eligible Draft PRs to Ready before submitting LGTM, automatically squash-merge the active identity's own PR after LGTM, and enforce head-SHA and merge gates.
---

# GitHub PR Review

Run a GitHub-native review with an auditable per-file trail. Treat analysis, review submission, approval, and merge as separate decisions.

## Required invariants

- Resolve and freeze the PR number, repository, base SHA, and head SHA before reviewing.
- Inspect every changed file. Read surrounding code, tests, callers, and project review rules when the diff alone is insufficient.
- Mark a file Viewed only after it has actually been reviewed. Never bulk-mark files merely to complete the checklist.
- Put actionable findings on the narrowest relevant diff lines. Include severity and confidence when project rules require them.
- Keep inline comments in a pending review until the whole PR has been assessed.
- Resolve a review conversation only after verifying at the frozen head SHA that its underlying finding is fully addressed. Never resolve an unfixed, partially fixed, uncertain, or merely acknowledged conversation.
- Submit `REQUEST_CHANGES` for any blocking finding, `COMMENT` for non-blocking feedback only, and `APPROVE` only when no blocking finding remains.
- Never approve a PR authored by the active GitHub identity as a substitute for independent approval.
- For a PR authored by the active GitHub identity, treat a completed LGTM review as authorization to squash-merge after every merge gate passes; do not ask for separate confirmation. For any other PR, never merge without explicit user authorization in the current request.
- Recheck the head SHA immediately before Submit and again before merge. Stop if it changed.
- When a completed review has no blocking finding, automatically mark an eligible Draft PR Ready before submitting LGTM. Keep it Draft after a blocking finding or when any Ready gate is unknown.
- Never bypass required checks, unresolved conversations, branch protection, or repository rules.

## Tool routing

1. Use the authenticated GitHub CLI (`gh`) first for PR identity, files, reviews, threads, checks, review writes, Ready state, and merge. Confirm `gh auth status` succeeds before relying on it.
2. Use `scripts/reviewctl.py` through a Python 3 runtime for HEAD-guarded pending review, Viewed, inline comment, conversation resolution, Ready, and Submit operations. The helper is the preferred `gh api` wrapper for those exact mutations.
3. Use local `git` only to inspect the checked-out code and determine repository context.
4. Use an authenticated GitHub connector or official GitHub MCP tool only as a fallback when `gh` and `reviewctl.py` cannot provide a required capability.
5. If neither authenticated `gh` nor a working fallback is available, complete a read-only local review if possible, but do not claim GitHub state was updated.

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

### 4. Classify findings and reconcile conversations

Aggregate findings without suppressing valid findings. For every unresolved review conversation:

1. Identify the concrete underlying finding and the commit or diff intended to address it.
2. Verify the fix against the frozen head SHA and run proportionate validation.
3. Resolve the conversation only when the finding is fully addressed and the relevant validation passes.
4. Leave the conversation unresolved when the fix is incomplete, uncertain, unverified, or only acknowledged. Preserve its blocking status when applicable.

Use the HEAD-guarded helper for each verified fix:

```bash
python3 <skill-dir>/scripts/reviewctl.py resolve-thread \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA \
  --thread-id THREAD_NODE_ID
```

Maintain a conversation ledger with `resolved`, `left unresolved`, and the reason for each decision. Re-read the threads after mutations and stop if pagination prevents a complete result.

Choose the intended review event:

- `REQUEST_CHANGES`: at least one blocking correctness, security, data-loss, compatibility, required-test issue, or unresolved blocking conversation remains.
- `COMMENT`: feedback exists but none is blocking, or the active identity is the author.
- `APPROVE`: all files are reviewed, no blocking finding remains, validation evidence is adequate, and approval was requested or is normal for the repository.

### 5. Promote an eligible Draft PR to Ready before LGTM

Treat skill invocation as authorization for this guarded Draft-to-Ready transition. Perform it before submitting a no-blocker LGTM review. Mark a Draft PR Ready only when all of these are true:

- every changed file has been reviewed;
- the intended event is `COMMENT` or `APPROVE`, and the current review has no blocking finding;
- every verified fixed conversation has been resolved and no unresolved blocking conversation remains;
- repository-specific pre-Ready gates are known and satisfied, including required validation, PR metadata, and temporary design-artifact disposition when applicable;
- the PR is still open and its head SHA still matches the reviewed SHA.

Non-blocking feedback does not prevent Ready. Keep the PR Draft and skip LGTM after a blocking finding, a failed required check, an unknown gate, a failed Ready transition, or a head change.

Use the HEAD-guarded helper:

```bash
python3 <skill-dir>/scripts/reviewctl.py mark-ready \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA
```

Verify GitHub reports `isDraft: false` before submitting LGTM. Treat an already-Ready PR as an idempotent success.

### 6. Submit one review

Recheck the head SHA, then submit the pending review with the event selected in step 4:

```bash
python3 <skill-dir>/scripts/reviewctl.py submit \
  --repo OWNER/REPO --pr NUMBER --expected-head HEAD_SHA \
  --review-id REVIEW_NODE_ID --event APPROVE \
  --body 'LGTM. Reviewed all changed files; no blocking findings.'
```

Submit `REQUEST_CHANGES` without promoting Ready when blockers remain. For a no-blocker review, submit LGTM only after the PR is confirmed Ready. Do not post a separate “LGTM” issue comment when the submitted review body already carries the conclusion.

For a PR authored by the active GitHub identity, submit `COMMENT` rather than self-approve. Treat the result as LGTM only when all files have been reviewed, no actionable finding or unresolved conversation remains, validation evidence is adequate, and the PR is Ready.

### 7. Merge under the applicable authorization

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
- conversation resolution result (`resolved/total`, with reasons for anything left unresolved);
- Draft-to-Ready result (`already ready`, `marked ready before LGTM`, or the exact reason it remained Draft);
- submitted review event (`COMMENT`, `REQUEST_CHANGES`, or `APPROVE`) and whether it was LGTM;
- checks and unresolved-thread status;
- whether merge was authorized by self-authored LGTM or explicit request, and whether the squash merge was performed;
- any action that could not be written to GitHub.

Do not say “LGTM”, “approved”, or “merged” unless GitHub confirms that exact state.

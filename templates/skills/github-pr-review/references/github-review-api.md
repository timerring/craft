# GitHub review API notes

Use these notes only when the official GitHub connector does not expose the required operation.

## Identity and frozen HEAD

Resolve PR identity with `gh pr view --json id,headRefOid,...`. Every write must compare the current `headRefOid` with the SHA frozen at review start. A mismatch invalidates the in-progress review decision.

## Pending review

Before creating anything, query the active actor's `PENDING` review. Reuse it when its commit OID matches the frozen HEAD. If it targets another HEAD, stop and require the stale review to be submitted or discarded. Only when no pending review exists, create one with GraphQL `addPullRequestReview`, passing `pullRequestId` and `commitOID` and omitting `event`. Keep the returned review node ID.

## Authentication preflight

Use the non-JSON form of `gh auth status --active --hostname HOST` when relying on its exit code. `gh auth status --json` intentionally exits zero even when an account has authentication problems, so JSON mode is safe only when the returned account state is explicitly inspected.

## Inline review threads

Add comments to that pending review using `addPullRequestReviewThread` and `pullRequestReviewId`. Use blob line numbers and `LEFT`/`RIGHT`; do not use deprecated diff-relative `position`.

For line comments, pass `path`, `line`, `side`, and `subjectType: LINE`. For a file-level comment, pass `path` and `subjectType: FILE` without a line.

## Viewed state

After reviewing one file, call `markFileAsViewed` with the pull request node ID and repository-relative path. Viewed is review progress, not a substitute for inspecting the file.

## Submit

Submit the pending review with `submitPullRequestReview`, the pending review node ID, a summary body, and exactly one event: `COMMENT`, `REQUEST_CHANGES`, or `APPROVE`.

## Ready state

After a no-blocker review satisfies repository Ready gates, recheck the frozen HEAD and call `markPullRequestReadyForReview` with the pull request node ID. The mutation is only needed when `isDraft` is true; otherwise treat the operation as an idempotent success. Re-read `isDraft` after the mutation before reporting Ready.

## Merge safety

For a PR authored by the active GitHub identity, a completed LGTM review authorizes squash merge under the skill. Any other PR requires explicit merge authorization in the current request. Before either merge path, re-read head SHA, required checks, review decision, unresolved threads, Draft state, mergeability, and branch protection. Prefer a merge API that accepts the expected head SHA. Treat missing or paginated-away evidence as an unknown gate and stop.

## Primary references

- GitHub GraphQL pull request mutations: https://docs.github.com/en/graphql/reference/pulls
- REST pull request reviews: https://docs.github.com/en/rest/pulls/reviews
- REST pull request merge: https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request
- GitHub PR review UI workflow: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request

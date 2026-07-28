# Issue Dependencies (Blocked By / Blocking)

Dependencies let you mark that an issue is blocked by another issue. This creates a formal dependency relationship visible in the UI and trackable via the GitHub CLI.

## Preferred commands

```bash
# Add relationships
gh issue edit ISSUE --repo OWNER/REPO --add-blocked-by BLOCKER
gh issue edit ISSUE --repo OWNER/REPO --add-blocking BLOCKED

# Remove relationships
gh issue edit ISSUE --repo OWNER/REPO --remove-blocked-by BLOCKER
gh issue edit ISSUE --repo OWNER/REPO --remove-blocking BLOCKED
```

Accept issue numbers or URLs for `BLOCKER` and `BLOCKED`.

## Advanced operations with `gh api`

**List issues blocking this issue:**
```bash
gh api repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by
```

**Add a blocking dependency by numeric database ID:**
```bash
gh api repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by \
  -X POST -F issue_id=12345
```

The `issue_id` is the numeric issue **ID**, not the issue number.

**Remove a blocking dependency by numeric database ID:**
```bash
gh api repos/{owner}/{repo}/issues/{issue_number}/dependencies/blocked_by/{issue_id} \
  -X DELETE
```

## Advanced GraphQL through `gh`

Run GraphQL only through `gh api graphql`:

```bash
gh api graphql -f query='{
  repository(owner: "OWNER", name: "REPO") {
    issue(number: 123) {
      blockedBy(first: 10) { nodes { number title state } }
      blocking(first: 10) { nodes { number title state } }
      issueDependenciesSummary { blockedBy blocking totalBlockedBy totalBlocking }
    }
  }
}'
```

**Add a dependency:**
```bash
gh api graphql -f query='mutation {
  addBlockedBy(input: {
    issueId: "BLOCKED_ISSUE_NODE_ID"
    blockingIssueId: "BLOCKING_ISSUE_NODE_ID"
  }) {
    blockingIssue { number title }
  }
}'
```

**Remove a dependency:**
```bash
gh api graphql -f query='mutation {
  removeBlockedBy(input: {
    issueId: "BLOCKED_ISSUE_NODE_ID"
    blockingIssueId: "BLOCKING_ISSUE_NODE_ID"
  }) {
    blockingIssue { number title }
  }
}'
```

## Tracked issues (read-only)

Task-list tracking relationships are available through `gh api graphql` as read-only fields:

- `trackedIssues(first: N)` - issues tracked in this issue's task list
- `trackedInIssues(first: N)` - issues whose task lists reference this issue

These are set automatically when issues are referenced in task lists (`- [ ] #123`). There are no mutations to manage them.

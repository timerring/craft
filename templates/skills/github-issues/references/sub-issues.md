# Sub-Issues and Parent Issues

Sub-issues let you break down work into hierarchical tasks. Each parent issue can have up to 100 sub-issues, nested up to 8 levels deep. Sub-issues can span repositories within the same owner.

## Recommended Workflow

Create a sub-issue directly with the GitHub CLI:

```bash
gh issue create --repo OWNER/REPO \
  --title "Sub-task title" \
  --body "Description" \
  --parent PARENT_NUMBER
```

Link or unlink existing issues with `gh issue edit`:

```bash
gh issue edit PARENT --repo OWNER/REPO --add-sub-issue CHILD
gh issue edit PARENT --repo OWNER/REPO --remove-sub-issue CHILD
gh issue edit CHILD --repo OWNER/REPO --parent PARENT
gh issue edit CHILD --repo OWNER/REPO --remove-parent
```

Use `gh api` only for listing or reprioritizing sub-issues.

## Advanced operations with `gh api`

**List sub-issues:**
```bash
gh api repos/{owner}/{repo}/issues/{issue_number}/sub_issues
```

**Get parent issue:**
```bash
gh api repos/{owner}/{repo}/issues/{issue_number}/parent
```

**Add an existing issue as a sub-issue:**
```bash
# sub_issue_id is the numeric issue ID (not the issue number)
# Get it from the .id field when creating or fetching an issue
gh api repos/{owner}/{repo}/issues/{parent_number}/sub_issues \
  -X POST -F sub_issue_id=12345
```

To move a sub-issue that already has a parent, add `-F replace_parent=true`.

**Remove a sub-issue:**
```bash
gh api repos/{owner}/{repo}/issues/{parent_number}/sub_issue \
  -X DELETE -F sub_issue_id=12345
```

**Reprioritize a sub-issue:**
```bash
gh api repos/{owner}/{repo}/issues/{parent_number}/sub_issues/priority \
  -X PATCH -F sub_issue_id=6 -F after_id=5
```

Use `after_id` or `before_id` to position the sub-issue relative to another.

## Advanced GraphQL through `gh api graphql`

**Read parent and sub-issues:**
```bash
gh api graphql -f query='{
  repository(owner: "OWNER", name: "REPO") {
    issue(number: 123) {
      parent { number title }
      subIssues(first: 50) {
        nodes { number title state }
      }
      subIssuesSummary { total completed percentCompleted }
    }
  }
}'
```

**Add a sub-issue:**
```bash
gh api graphql -f query='mutation {
  addSubIssue(input: {
    issueId: "PARENT_NODE_ID"
    subIssueId: "CHILD_NODE_ID"
  }) {
    issue { id }
    subIssue { id number title }
  }
}'
```

You can also use `subIssueUrl` instead of `subIssueId` (pass the issue's HTML URL). Add `replaceParent: true` to move a sub-issue from another parent.

**Create an issue directly as a sub-issue:**
```bash
gh api graphql -f query='mutation {
  createIssue(input: {
    repositoryId: "REPO_NODE_ID"
    title: "Implement login validation"
    parentIssueId: "PARENT_NODE_ID"
  }) {
    issue { id number }
  }
}'
```

**Remove a sub-issue:**
```bash
gh api graphql -f query='mutation {
  removeSubIssue(input: {
    issueId: "PARENT_NODE_ID"
    subIssueId: "CHILD_NODE_ID"
  }) {
    issue { id }
  }
}'
```

**Reprioritize a sub-issue:**
```bash
gh api graphql -f query='mutation {
  reprioritizeSubIssue(input: {
    issueId: "PARENT_NODE_ID"
    subIssueId: "CHILD_NODE_ID"
    afterId: "OTHER_CHILD_NODE_ID"
  }) {
    issue { id }
  }
}'
```

Use `afterId` or `beforeId` to position relative to another sub-issue.

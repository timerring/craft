# Issue Types (Advanced GraphQL)

Issue types (Bug, Feature, Task, Epic, etc.) are defined at the **organization** level and inherited by repositories. They categorize issues beyond labels.

For basic usage, use `gh issue create --type NAME`, `gh issue edit NUMBER --type NAME`, `gh issue edit NUMBER --remove-type`, or `gh issue list --type NAME`. Use `gh api graphql` only for advanced discovery or mutations.

## GraphQL Feature Header

All advanced GraphQL issue type operations require the `GraphQL-Features: issue_types` HTTP header. Pass it with `gh api graphql -H`.

## List types (org or repo level)

```bash
gh api graphql -H 'GraphQL-Features: issue_types' -f query='{
  organization(login: "OWNER") {
    issueTypes(first: 20) {
      nodes { id name color description isEnabled }
    }
  }
}'
```

Types can also be listed per-repo via `repository.issueTypes` or looked up by name via `repository.issueType(name: "Bug")`.

## Read an issue's type

```bash
gh api graphql -H 'GraphQL-Features: issue_types' -f query='{
  repository(owner: "OWNER", name: "REPO") {
    issue(number: 123) {
      issueType { id name color }
    }
  }
}'
```

## Set type on an existing issue

```bash
gh api graphql -H 'GraphQL-Features: issue_types' -f query='mutation {
  updateIssueIssueType(input: {
    issueId: "ISSUE_NODE_ID"
    issueTypeId: "IT_xxx"
  }) {
    issue { id issueType { name } }
  }
}'
```

## Create issue with type

```bash
gh api graphql -H 'GraphQL-Features: issue_types' -f query='mutation {
  createIssue(input: {
    repositoryId: "REPO_NODE_ID"
    title: "Fix login bug"
    issueTypeId: "IT_xxx"
  }) {
    issue { id number issueType { name } }
  }
}'
```

To clear the type, set `issueTypeId` to `null`.

## Available colors

`GRAY`, `BLUE`, `GREEN`, `YELLOW`, `ORANGE`, `RED`, `PINK`, `PURPLE`

---
name: github-issues
description: 'Create, update, search, and manage GitHub issues using the authenticated GitHub CLI (`gh`) only. Use this skill when users want to create bug reports, feature requests, or task issues, update existing issues, add labels/assignees/milestones, set issue fields (dates, priority, custom fields), set issue types, manage issue workflows, link issues, add dependencies, or track blocked-by/blocking relationships. Triggers on requests like "create an issue", "file a bug", "request a feature", "update issue X", "set the priority", "set the start date", "link issues", "add dependency", "blocked by", "blocking", or any GitHub issue management task.'
---

# GitHub Issues

Manage GitHub issues exclusively through the authenticated GitHub CLI (`gh`).

## Required tool routing

- Run `gh auth status` before relying on GitHub access. Stop and report the authentication problem if it fails.
- Use `gh issue` for ordinary issue reads and writes.
- Use `gh search issues` for cross-repository or text search.
- Use `gh api` only when the required operation is not exposed by a higher-level `gh issue`, `gh search`, or `gh project` command.
- Use `gh api graphql` for Projects V2 or advanced fields that require GraphQL.
- Do not switch to another GitHub access route.

| Operation | Preferred command |
|-----------|-------------------|
| View issue | `gh issue view NUMBER --repo OWNER/REPO --json ...` |
| List issues | `gh issue list --repo OWNER/REPO --state all --json ...` |
| Search issues | `gh search issues QUERY --repo OWNER/REPO --json ...` |
| Create issue | `gh issue create --repo OWNER/REPO --title ... --body ...` |
| Update issue | `gh issue edit NUMBER --repo OWNER/REPO ...` |
| Add comment | `gh issue comment NUMBER --repo OWNER/REPO --body ...` |
| Close/reopen | `gh issue close NUMBER --repo OWNER/REPO` / `gh issue reopen NUMBER --repo OWNER/REPO` |
| Advanced API operation | `gh api ...` or `gh api graphql ...` |

## Workflow

1. **Determine action**: Create, update, or query?
2. **Gather context**: Use `gh` to get repository info, existing issues, labels, milestones, and templates as needed
3. **Structure content**: Use appropriate template from [references/templates.md](references/templates.md)
4. **Execute**: Use the highest-level applicable `gh` command
5. **Confirm**: Report the issue URL to user

## Creating Issues

Use `gh issue create`. It supports issue types, projects, parents, and dependency relationships.

```bash
gh issue create --repo OWNER/REPO \
  --title "Issue title" \
  --body "Issue body in markdown" \
  --type "Bug"
```

### Optional Parameters

Add any applicable flags:

```
--type "Bug"                     # Issue type (Bug, Feature, Task, Epic, etc.)
--label "bug"                    # Label name; repeat for multiple
--assignee "username"            # Assignee login
--milestone "v1.0"               # Milestone title
--project "Roadmap"              # Project title
--parent 123                     # Parent issue number or URL
--blocked-by 200,201             # Issues blocking the new issue
--blocking 300                   # Issues blocked by the new issue
```

**Issue types** are organization-level metadata. To discover available types, use:
```bash
gh api graphql -f query='{ organization(login: "ORG") { issueTypes(first: 10) { nodes { name } } } }' --jq '.data.organization.issueTypes.nodes[].name'
```

**Prefer issue types over labels for categorization.** When issue types are available (e.g., Bug, Feature, Task), use the `type` parameter instead of applying equivalent labels like `bug` or `enhancement`. Issue types are the canonical way to categorize issues on GitHub. Only fall back to labels when the org has no issue types configured.

### Title Guidelines

- Be specific and actionable
- Keep under 72 characters
- When issue types are set, don't add redundant prefixes like `[Bug]`
- Examples:
  - `Login fails with SSO enabled` (with type=Bug)
  - `Add dark mode support` (with type=Feature)
  - `Add unit tests for auth module` (with type=Task)

### Body Structure

Always use the templates in [references/templates.md](references/templates.md). Choose based on issue type:

| User Request | Template |
|--------------|----------|
| Bug, error, broken, not working | Bug Report |
| Feature, enhancement, add, new | Feature Request |
| Task, chore, refactor, update | Task |

## Updating Issues

Use `gh issue edit` and include only fields that should change:

```bash
gh issue edit NUMBER --repo OWNER/REPO \
  --title "Updated title" \
  --type "Bug"
```

Use `gh issue close` or `gh issue reopen` for state transitions. `gh issue edit` supports title, body, type, labels, assignees, milestone, projects, parent, sub-issues, and dependency relationships.

## Examples

### Example 1: Bug Report

**User**: "Create a bug issue - the login page crashes when using SSO"

**Action**:
```bash
gh issue create --repo github/awesome-copilot \
  --title "Login page crashes when using SSO" \
  --type "Bug" \
  --body "## Description
The login page crashes when users attempt to authenticate using SSO.

## Steps to Reproduce
1. Navigate to login page
2. Click 'Sign in with SSO'
3. Page crashes

## Expected Behavior
SSO authentication should complete and redirect to dashboard.

## Actual Behavior
Page becomes unresponsive and displays error."
```

### Example 2: Feature Request

**User**: "Create a feature request for dark mode with high priority"

**Action**:
```bash
gh issue create --repo github/awesome-copilot \
  --title "Add dark mode support" \
  --type "Feature" \
  --label "high-priority" \
  --body "## Summary
Add dark mode theme option for improved user experience and accessibility.

## Motivation
- Reduces eye strain in low-light environments
- Increasingly expected by users

## Proposed Solution
Implement theme toggle with system preference detection.

## Acceptance Criteria
- [ ] Toggle switch in settings
- [ ] Persists user preference
- [ ] Respects system preference by default"
```

## Common Labels

Use these standard labels when applicable:

| Label | Use For |
|-------|---------|
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `documentation` | Documentation updates |
| `good first issue` | Good for newcomers |
| `help wanted` | Extra attention needed |
| `question` | Further information requested |
| `wontfix` | Will not be addressed |
| `duplicate` | Already exists |
| `high-priority` | Urgent issues |

## Tips

- Always confirm the repository context before creating issues
- Ask for missing critical information rather than guessing
- Link related issues when known: `Related to #123`
- For updates, fetch current issue first to preserve unchanged fields

## Extended Capabilities

The following features may require `gh api` or `gh api graphql` beyond the basic `gh issue` commands. Each is documented in its own reference file so the agent only loads the knowledge it needs.

| Capability | When to use | Reference |
|------------|-------------|-----------|
| Advanced search | Complex queries with boolean logic, date ranges, cross-repo search, issue field filters (`field.name:value`) | [references/search.md](references/search.md) |
| Sub-issues & parent issues | Breaking work into hierarchical tasks | [references/sub-issues.md](references/sub-issues.md) |
| Issue dependencies | Tracking blocked-by / blocking relationships | [references/dependencies.md](references/dependencies.md) |
| Issue types (advanced) | GraphQL operations beyond `gh issue --type` | [references/issue-types.md](references/issue-types.md) |
| Projects V2 | Project boards, progress reports, field management | [references/projects.md](references/projects.md) |
| Issue fields | Custom metadata: dates, priority, text, numbers (private preview) | [references/issue-fields.md](references/issue-fields.md) |
| Images in issues | Embedding images in issue bodies and comments via CLI | [references/images.md](references/images.md) |

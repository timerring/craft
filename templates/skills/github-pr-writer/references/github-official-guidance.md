# GitHub official PR guidance

GitHub does not prescribe one universal mandatory PR body. Repository-specific contribution guidelines and pull request templates define the local contract.

GitHub's current guidance recommends:

- Keep pull requests small and focused; split changes that serve independent purposes.
- Provide a clear title and description covering the problem, approach, result, and areas needing reviewer attention.
- Self-review the diff and confirm relevant builds or tests before requesting review.
- Highlight security implications for dependencies, authentication, permissions, workflows, and sensitive data.
- Link related issues or projects and use status labels or Draft PRs to communicate readiness.
- Use pull request templates to request consistent context such as purpose, related issues, testing notes, and checklists.

Primary official sources:

- Helping others review your changes: https://docs.github.com/en/pull-requests/concepts/helping-others-review-your-changes
- Managing and standardizing pull requests: https://docs.github.com/en/pull-requests/reference/managing-and-standardizing-pull-requests
- Creating a pull request template: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
- Linking a pull request to an issue: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue
- About pull requests and Draft PRs: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests

## Conventional Commits

This skill additionally requires PR titles to follow Conventional Commits 1.0.0 so that squash-merge commit subjects remain machine-readable:

```text
<type>[optional scope][!]: <description>
```

The specification requires a type plus `: ` and a description. `feat` represents a feature, `fix` represents a bug fix, scopes are optional, other types are allowed, and breaking changes use `!` before the colon or a `BREAKING CHANGE:` footer.

Official specification:

- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/

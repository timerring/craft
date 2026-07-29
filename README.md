<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/headerDark.svg" />
    <img src="assets/headerLight.svg" alt="CRAFT" />
  </picture>

**C**ollection of **R**aw **A**I **F**irst **T**emplates.

*My Personal AI templates and configurations.*

</div>

## Structure

```
craft/
├── shortcuts/         # Quick prompt shortcuts
│   └── *.md           # PPLX shortcuts
└── templates/         # Reusable templates
    ├── mcp/           # MCP server configs
    │   ├── mcp.json   # Server configuration
    │   └── mcp.md     # Server documentation
    ├── rules/         # AI behavior rules
    │   └── coding.md  # Coding rules
    ├── skills/        # Reusable Codex skills
    │   ├── github-issues/
    │   │   ├── SKILL.md
    │   │   └── references/  # Issue APIs, templates, and workflows
    │   ├── github-pr-review/
    │   │   ├── SKILL.md
    │   │   ├── agents/openai.yaml
    │   │   ├── references/github-review-api.md
    │   │   └── scripts/  # GitHub review helper and tests
    │   ├── github-pr-writer/
    │   │   ├── SKILL.md
    │   │   ├── agents/openai.yaml
    │   │   └── references/github-official-guidance.md
    │   └── github-release-writer/
    │       ├── SKILL.md
    │       └── agents/openai.yaml
    └── workflows/     # Task workflows
        └── index-code.md  # Code indexing workflow
```

## Contents

### Rules
Global constraints for AI behavior:
- ASCII only output
- Command execution policy
- Code editing guidelines
- Debugging approach
- Efficiency rules

### MCP
MCP server configurations with documentation for 11 servers:
- chrome-devtools, dart, figma, proxyman
- Context7, tavily-mcp, morph
- sequential-thinking, mcp-server-time, serena, pencil

### Workflows
Step-by-step templates:
- Code indexing with security analysis
- Malicious code detection
- Weak password handling

### Skills
Reusable Codex skills:
- `github-issues`: creates, updates, searches, and manages GitHub issues exclusively through the authenticated GitHub CLI, including issue types, fields, Projects V2, sub-issues, and dependency relationships.[^github-issues-source]
- `github-pr-review`: reviews every changed file in a GitHub PR, tracks files as Viewed, collects inline feedback in a pending review, promotes eligible Draft PRs to Ready, stops after LGTM for explicit user confirmation, and guards approval and any later merge with frozen-HEAD and repository checks.
- `github-pr-writer`: inspects repository guidance and the actual diff, then creates or updates a GitHub PR with a Conventional Commits title, evidence-based description, scoped commit, verification, and reviewer guidance.
- `github-release-writer`: drafts and reviews user-facing GitHub Release notes from repository evidence, highlights breaking changes and upgrade risks, and keeps drafting separate from explicit publication.

[^github-issues-source]: Adapted from GitHub's [`github-issues` skill](https://github.com/github/awesome-copilot/tree/main/skills/github-issues) in `github/awesome-copilot`, with its MCP-based operations replaced by authenticated `gh` CLI-only routing.

### Shortcuts
PPLX shortcuts for Perplexity AI prompts.


## Usage

Copy templates to your AI assistant's configuration directory and customize as needed.

To install the GitHub skills for the current user while keeping this repository as the source of truth:

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/templates/skills/github-issues" ~/.agents/skills/github-issues
ln -s "$(pwd)/templates/skills/github-pr-review" ~/.agents/skills/github-pr-review
ln -s "$(pwd)/templates/skills/github-pr-writer" ~/.agents/skills/github-pr-writer
ln -s "$(pwd)/templates/skills/github-release-writer" ~/.agents/skills/github-release-writer
```

Use `$github-issues` when asking Codex to create, update, search, or organize GitHub issues.
Use `$github-pr-review` when asking Codex to review, approve, or merge a pull request. The skill requires an authenticated GitHub CLI (`gh auth status`) for GitHub write operations.
Use `$github-pr-writer` to turn the intended repository changes into a scoped commit and a created or updated pull request. It uses the authenticated GitHub CLI (`gh`) exclusively for GitHub operations; ask for text only when you do not want GitHub changes.
Use `$github-release-writer` to draft or review release notes from tags, commits, pull requests, and changelogs; publishing requires an explicit request.

## License

MIT

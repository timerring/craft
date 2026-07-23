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
    │   └── github-pr-review/
    │       ├── SKILL.md
    │       ├── agents/openai.yaml
    │       ├── references/github-review-api.md
    │       └── scripts/  # GitHub review helper and tests
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
- `github-pr-review`: reviews every changed file in a GitHub PR, tracks files as Viewed, collects inline feedback in a pending review, promotes eligible Draft PRs to Ready, automatically squash-merges the active identity's own PR after LGTM, and guards approval and merge operations with frozen-HEAD and repository checks.

### Shortcuts
PPLX shortcuts for Perplexity AI prompts.


## Usage

Copy templates to your AI assistant's configuration directory and customize as needed.

To install the GitHub PR review skill for the current user while keeping this repository as the source of truth:

```bash
mkdir -p ~/.agents/skills
ln -s "$(pwd)/templates/skills/github-pr-review" ~/.agents/skills/github-pr-review
```

Use `$github-pr-review` when asking Codex to review, approve, or merge a pull request. The skill requires an authenticated GitHub CLI (`gh auth status`) for GitHub write operations.

## License

MIT

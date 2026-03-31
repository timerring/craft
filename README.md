# craft

**C**ollection of **R**aw **A**I **F**irst **T**emplates.

> My Personal AI templates and configurations.

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

### Shortcuts
PPLX shortcuts for Perplexity AI prompts.


## Usage

Copy templates to your AI assistant's configuration directory and customize as needed.

## License

MIT

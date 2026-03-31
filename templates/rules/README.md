# Rules

Global constraints for AI assistant behavior, execution policy, and output style.

## Purpose

Rules for AI assistant behavior in coding tasks:

- **ASCII Only** - No emojis, em dashes, smart quotes, Unicode bullets
- **Index rules** - Command execution, file write, MCP usage, password handling
- **Code Rules** - Read before edit, no premature abstractions, stop on failure
- **Debugging Rules** - Read code first, state findings, do not guess
- **Approach** - Think before acting, be concise, prefer editing over rewriting
- **Efficiency** - Read before writing, test once, verify once

## Files

| File | Purpose |
|------|---------|
| `coding.md` | Code editing, debugging, and execution rules |

## References

Inspired by and adapted from:

- [claude-token-efficient](https://github.com/drona23/claude-token-efficient) - One file that cuts Claude output verbosity by ~63%

## Usage

Copy relevant rules to your AI assistant's configuration:

- **Claude Code**: Project root as `CLAUDE.md`
- **Cursor**: `.cursorrules`
- **Windsurf**: `.windsurf/rules/`

## Contributing

Found a behavior these rules can fix?

1. The annoying behavior (what the AI does by default)
2. The prompt that triggers it
3. The fix rule you propose

Community submissions welcome.

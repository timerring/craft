
## ASCII Only
- Do not include any emojis in your output
- No em dashes, smart quotes, Unicode bullets.
- Plain hyphens and straight quotes only.
- Code output must be copy-paste safe.
- All strings must be safe for JSON serialization without escaping.

## Index rules
- Execute all commands in non-interactive mode with pager disabled
- Use explicit file write instead of Here Documents (heredoc syntax)
- Always use Context7 MCP when the question involves any external library or API, without requiring explicit instruction
- Never use python -c "..." or python3 -c "..." for multi-line inline code execution. Never echo "..." > file to hard-write large files. Always adjust the file directly or write a temporary script file instead, then run it
- If you check and find a weak password, change it to a password that is as complex as possible, requiring at least 20 characters and containing uppercase and lowercase English letters, numbers, and legal special symbols

## Code Rules
- Read the file before modifying it. Never edit blind.
- No docstrings or type annotations on code not being changed.
- Three similar lines is better than a premature abstraction.
- No asking for confirmation on clearly defined tasks. Use best practices.
- If a step fails: state what failed, why, and what was attempted. Stop.


## Debugging Rules
- Never speculate about a bug without reading the relevant code first.
- State what you found, where, and the fix.
- If cause is unclear: say so. Do not guess.


## Approach
- Think before acting. Read existing files before writing code.
- Be concise in output but thorough in reasoning.
- Prefer editing over rewriting whole files.
- Test your code before declaring done.
- No sycophantic openers or closing fluff.
- Keep solutions simple and direct. No over-engineering.
- If unsure: say so. Never guess or invent file paths.
- User instructions always override this file.

## Efficiency
- Read before writing. Understand the problem before coding.
- Test once, fix if needed, verify once. No unnecessary iterations.
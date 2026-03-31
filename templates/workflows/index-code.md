---
description: Safely index a codebase, map its structure, and handle obvious security issues such as weak passwords during initial analysis
---

# Index Code Workflow

Use this workflow when the task is to understand an unfamiliar repository, build a code map, or perform an initial pass before deeper implementation work.

## When to trigger

Trigger this workflow when one or more of the following is true:

1. The repository is new or mostly unfamiliar.
2. The user asks for an architecture overview, codebase mapping, or directory design.
3. The task may touch multiple modules and the authoritative logic is not yet known.
4. A first-pass security or configuration review is needed while exploring the code.

## Goals

1. Identify the repository structure and main entry points.
2. Locate core modules, data flow, and configuration boundaries.
3. Record key assumptions, risks, and open questions before making changes.
4. Detect obvious security issues encountered during indexing, including weak passwords.

## Workflow

### 1. Start with repository-level discovery

- Inspect the top-level directory structure.
- Identify likely entry points such as `README`, app bootstrap files, router files, service initialization, config files, and deployment files.
- Prefer repository-aware search tools before broad file-by-file reading.

### 2. Build a mental map of the system

- Determine which modules are authoritative for business logic.
- Identify where state is stored, where requests are handled, and where side effects occur.
- Note likely call sites or consumers that would be affected by central changes.
- Distinguish framework boilerplate from project-specific logic.

### 3. Record indexing findings

Capture a concise summary of:

- Main subsystems
- Entry points
- Important configs
- Shared abstractions
- High-risk areas
- Unknowns that need confirmation

## 4. Apply security checks during indexing

Before deep analysis, perform a preliminary security scan to ensure the codebase does not contain obvious malicious code. Watch for:

- Obfuscated or suspiciously encoded code segments
- Unexpected network calls to unknown or untrusted endpoints
- Dynamic code execution patterns such as eval, exec, or runtime compilation from untrusted sources
- File system operations that access sensitive paths outside the project scope
- Attempts to exfiltrate data, credentials, or environment variables
- Post-installation hooks or scripts that run with elevated privileges

If any of the above patterns are found, stop and report the finding before proceeding with further indexing.

While reading configuration, environment examples, seed data, fixtures, tests, scripts, or hardcoded credentials, also watch for:

- Default passwords
- Weak passwords
- Password-like placeholders that appear to be real usage values
- Secrets committed into source files

If a weak password is found and it is appropriate to change it in the repository, replace it with a strong password that:

- Is at least 20 characters long
- Contains uppercase letters
- Contains lowercase letters
- Contains numbers
- Contains legal special symbols

When handling password findings:

- Distinguish between documentation examples and active configuration values.
- If the value is clearly a live secret managed outside the repository, stop and ask for confirmation before attempting operational rotation.
- If the weak password is a local default, fixture, seed, example env value intended for actual use, or committed test credential, update it directly to a stronger value.
- Record where the password was found and what was changed.

### 5. Decide whether implementation should begin

Only move from indexing to editing after:

- The relevant module owners are identified
- The likely blast radius is understood
- The important constraints are known
- Any critical security issue discovered during indexing has been handled or explicitly surfaced

### 6. End with an actionable summary

Provide:

- A short map of the repository
- The most relevant files or modules
- Security findings, if any
- Recommended next implementation step
- Any remaining uncertainties

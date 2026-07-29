---
name: github-release-writer
description: Draft, revise, review, or prepare user-facing GitHub Release notes from Git tags, commits, pull requests, changelogs, or supplied change lists. Use when asked to write a release, improve release notes, summarize changes between versions, prepare an upgrade announcement, assess release-note quality, configure GitHub-generated release notes, or create a GitHub Release. Covers breaking changes, features, fixes, security, upgrade guidance, known issues, assets, contributors, and changelog links.
---

# Write GitHub Release

Produce release notes that let a user quickly understand what changed, whether upgrading is risky, and what action to take.

## Guardrails

- Treat drafting, reviewing, and publishing as different actions.
- For a drafting or review request, use read-only inspection and return Markdown. Do not create tags, push commits, upload assets, or publish a Release.
- Perform an external mutation only when the user explicitly asks for it. Before publishing, resolve the repository, version, target commit, previous tag, prerelease/latest status, and assets.
- Preserve factual accuracy. Do not invent compatibility claims, performance numbers, CVE impact, contributors, migration steps, or known issues.
- Label an inference as an inference. Call out missing information that materially affects safe upgrading.
- Never expose private issue, vulnerability, or embargoed security details in public notes.

## Workflow

### 1. Establish the release range

Determine:

- repository and intended audience
- version and release status: stable, beta, release candidate, or prerelease
- target tag or commit
- previous release tag
- available artifacts and installation channels

When working in a local repository, inspect existing tags and history before choosing a range. Prefer an explicit range supplied by the user. If none is supplied, infer the most likely previous release and clearly state the assumption.

Useful read-only commands include:

```bash
git tag --sort=-version:refname
git log --first-parent --oneline PREVIOUS_TAG..TARGET
git diff --stat PREVIOUS_TAG..TARGET
gh pr list --state merged --limit 100 --json number,title,url,author,labels,mergedAt
```

Adapt the commands to the repository. Do not assume every commit corresponds to one user-visible change.

### 2. Build a change inventory

Use the strongest available evidence in this order:

1. merged pull requests and their labels/descriptions
2. changelog or migration documentation
3. commits and diffs
4. a user-supplied change list

Deduplicate related commits and PRs into one user-visible change. Separate:

- breaking changes
- features
- improvements and performance
- bug fixes
- security changes
- deprecations
- documentation
- dependencies and internal maintenance

Omit internal maintenance unless users need to know about it. Do not turn the release into an unedited commit dump.

### 3. Identify upgrade risk

Look specifically for:

- removed or renamed APIs
- changed defaults or behavior
- configuration or environment-variable changes
- schema, data-format, or storage migrations
- changed runtime or platform requirements
- deprecations
- security-sensitive changes
- rollback limitations

Put breaking changes before ordinary features. For each breaking change, state what changed, who is affected, and the exact migration action. If evidence supports it, explicitly say there are no breaking changes.

### 4. Write for users

Start with a two-to-four-sentence summary of the release's value. Describe outcomes rather than implementation details.

Prefer:

> Large projects now start faster because dependency discovery is cached.

Avoid:

> Refactored the resolver and added a cache map.

Link entries to their PRs or issues when URLs are available. Group small related fixes. Mention contributors without overstating authorship.

### 5. Add operational details

Include only the sections relevant to the project:

- installation or upgrade commands
- migration and rollback steps
- supported runtime/platform changes
- known issues and workarounds
- downloadable assets, platform/architecture names, checksums, signatures, or attestations
- container image and immutable digest
- full comparison link

Use semantic versioning when it fits the project's established convention:

- major: incompatible change
- minor: backward-compatible feature
- patch: backward-compatible fix

Do not impose semantic versioning on a repository that uses another documented scheme.

## Default output

Adapt this structure rather than emitting empty sections:

````markdown
# vX.Y.Z

Brief user-facing summary of the release and its most important outcome.

## Breaking changes

- **Change** — Who is affected and how to migrate. (#123)

## Features

- Added user-visible capability. (#124)

## Improvements

- Improved an existing workflow or measurable behavior. (#125)

## Bug fixes

- Fixed the symptom users experienced. (#126)

## Security

- Describe the safe public impact and required action. Avoid embargoed details.

## Upgrade

```sh
project-specific upgrade command
```

Include migration, compatibility, and rollback notes.

## Known issues

- Known limitation and workaround.

**Full changelog:** `vPREVIOUS...vX.Y.Z`
````

For a small patch release, prefer a compact summary plus fixes and full changelog. For a major release, emphasize migration, compatibility, and rollback.

## Review checklist

Before returning or publishing a release, verify:

- The tag and comparison range are correct.
- The summary explains user value.
- Breaking changes and required actions are prominent.
- Entries describe behavior, not only implementation.
- Claims are supported by repository evidence.
- Upgrade commands and compatibility requirements are accurate.
- Known issues and security information are safe to publish.
- PR, issue, migration-guide, and changelog links resolve.
- Prerelease/latest status and attached assets match the version.
- The notes contain no secrets or private references.

When reviewing existing notes, report the highest-risk omissions first and then provide a revised version.

## GitHub-generated release notes

When asked to configure automatic categorization, create or update `.github/release.yml`. Match categories to labels already used by the repository; do not invent a label taxonomy without checking it.

Minimal example:

```yaml
changelog:
  exclude:
    labels:
      - ignore-for-release
  categories:
    - title: Breaking Changes
      labels:
        - breaking-change
        - Semver-Major
    - title: Features
      labels:
        - enhancement
        - Semver-Minor
    - title: Fixes
      labels:
        - bug
        - Semver-Patch
    - title: Other Changes
      labels:
        - "*"
```

Treat generated notes as a draft. Manually add the release summary, migration guidance, known issues, and any operational details that cannot be derived from PR metadata.

## Official guidance

If the user asks what GitHub currently recommends, verify against current GitHub documentation and cite primary sources. Start with:

- Releases overview: <https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases>
- Automatically generated release notes: <https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes>
- Immutable releases: <https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases>

Distinguish GitHub features from community conventions. Semantic Versioning, Keep a Changelog, and Conventional Commits may be useful, but they are not GitHub Release specifications.

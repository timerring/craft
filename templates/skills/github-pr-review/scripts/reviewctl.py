#!/usr/bin/env python3
"""HEAD-guarded GitHub pull-request review state operations via `gh api`."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
from typing import Any, Sequence


class ReviewCtlError(RuntimeError):
    pass


def gh_binary() -> str:
    candidates = (
        os.environ.get("GH_BIN"),
        shutil.which("gh"),
        "/opt/homebrew/bin/gh",
        "/usr/local/bin/gh",
    )
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise ReviewCtlError("GitHub CLI `gh` is not installed or not on PATH")


def run_gh(args: Sequence[str], *, parse_json: bool = True) -> Any:
    proc = subprocess.run(
        [gh_binary(), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        message = proc.stderr.strip() or proc.stdout.strip() or "unknown gh failure"
        raise ReviewCtlError(message)
    output = proc.stdout.strip()
    if not parse_json:
        return output or None
    if not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise ReviewCtlError(f"expected JSON from gh, received: {output}") from exc


def ensure_auth() -> None:
    hostname = os.environ.get("GH_HOST", "github.com")
    run_gh(
        ["auth", "status", "--active", "--hostname", hostname],
        parse_json=False,
    )


def pr_identity(repo: str, pr: int) -> dict[str, Any]:
    result = run_gh(
        [
            "pr",
            "view",
            str(pr),
            "--repo",
            repo,
            "--json",
            "id,headRefOid,url,author,isDraft,state",
        ]
    )
    if not isinstance(result, dict):
        raise ReviewCtlError("GitHub returned an invalid pull request identity")
    return result


def require_head(repo: str, pr: int, expected_head: str) -> dict[str, Any]:
    identity = pr_identity(repo, pr)
    actual = identity.get("headRefOid")
    if actual != expected_head:
        raise ReviewCtlError(
            f"pull request HEAD changed: expected {expected_head}, found {actual}; restart review"
        )
    if identity.get("state") != "OPEN":
        raise ReviewCtlError(f"pull request is not open: {identity.get('state')}")
    return identity


def graphql(query: str, variables: dict[str, Any]) -> Any:
    args = ["api", "graphql", "-f", f"query={query}"]
    for name, value in variables.items():
        flag = "-F" if isinstance(value, (bool, int)) else "-f"
        args.extend([flag, f"{name}={value}"])
    return run_gh(args)


def find_pending_review(repo: str, pr: int) -> dict[str, Any] | None:
    parts = repo.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise ReviewCtlError("--repo must use OWNER/REPO format")
    owner, name = parts
    query = """
query($owner: String!, $name: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviews(first: 100, states: [PENDING]) {
        nodes { id state commit { oid } author { login } }
        pageInfo { hasNextPage }
      }
    }
  }
}
"""
    result = graphql(query, {"owner": owner, "name": name, "number": pr})
    viewer = result["data"]["viewer"]["login"]
    reviews = result["data"]["repository"]["pullRequest"]["reviews"]
    if reviews["pageInfo"]["hasNextPage"]:
        raise ReviewCtlError("pending review lookup was truncated; refusing to create a duplicate")
    matches = [
        review
        for review in reviews["nodes"]
        if review.get("author", {}).get("login") == viewer
    ]
    if len(matches) > 1:
        raise ReviewCtlError("GitHub returned multiple pending reviews for the active actor")
    return matches[0] if matches else None


def create_pending(repo: str, pr: int, expected_head: str) -> dict[str, Any]:
    identity = require_head(repo, pr, expected_head)
    existing = find_pending_review(repo, pr)
    if existing is not None:
        existing_head = existing.get("commit", {}).get("oid")
        if existing_head != expected_head:
            raise ReviewCtlError(
                "an existing pending review targets a different HEAD; discard or submit it "
                "before restarting the review"
            )
        return existing
    query = """
mutation($pullRequestId: ID!, $commitOID: GitObjectID!) {
  addPullRequestReview(input: {
    pullRequestId: $pullRequestId,
    commitOID: $commitOID
  }) {
    pullRequestReview { id state commit { oid } }
  }
}
"""
    result = graphql(
        query,
        {"pullRequestId": identity["id"], "commitOID": expected_head},
    )
    return result["data"]["addPullRequestReview"]["pullRequestReview"]


def mark_viewed(repo: str, pr: int, expected_head: str, path: str) -> dict[str, Any]:
    identity = require_head(repo, pr, expected_head)
    query = """
mutation($pullRequestId: ID!, $path: String!) {
  markFileAsViewed(input: {pullRequestId: $pullRequestId, path: $path}) {
    pullRequest { id headRefOid }
  }
}
"""
    result = graphql(query, {"pullRequestId": identity["id"], "path": path})
    return result["data"]["markFileAsViewed"]["pullRequest"]


def add_comment(
    repo: str,
    pr: int,
    expected_head: str,
    review_id: str,
    path: str,
    body: str,
    subject_type: str,
    line: int | None,
    side: str | None,
    start_line: int | None,
    start_side: str | None,
) -> dict[str, Any]:
    require_head(repo, pr, expected_head)
    if subject_type == "LINE" and (line is None or side is None):
        raise ReviewCtlError("LINE comments require --line and --side")
    if subject_type == "FILE" and any(
        value is not None for value in (line, side, start_line, start_side)
    ):
        raise ReviewCtlError("FILE comments must not include line or side arguments")
    if (start_line is None) != (start_side is None):
        raise ReviewCtlError("--start-line and --start-side must be supplied together")

    declarations = [
        "$reviewId: ID!",
        "$body: String!",
        "$path: String!",
        "$subjectType: PullRequestReviewThreadSubjectType!",
    ]
    fields = [
        "pullRequestReviewId: $reviewId",
        "body: $body",
        "path: $path",
        "subjectType: $subjectType",
    ]
    variables: dict[str, Any] = {
        "reviewId": review_id,
        "body": body,
        "path": path,
        "subjectType": subject_type,
    }
    for name, gql_name, gql_type, value in (
        ("line", "line", "Int!", line),
        ("side", "side", "DiffSide!", side),
        ("startLine", "startLine", "Int!", start_line),
        ("startSide", "startSide", "DiffSide!", start_side),
    ):
        if value is not None:
            declarations.append(f"${name}: {gql_type}")
            fields.append(f"{gql_name}: ${name}")
            variables[name] = value

    query = f"""
mutation({', '.join(declarations)}) {{
  addPullRequestReviewThread(input: {{{', '.join(fields)}}}) {{
    thread {{ id isResolved path line }}
  }}
}}
"""
    result = graphql(query, variables)
    return result["data"]["addPullRequestReviewThread"]["thread"]


def resolve_thread(
    repo: str,
    pr: int,
    expected_head: str,
    thread_id: str,
) -> dict[str, Any]:
    identity = require_head(repo, pr, expected_head)
    lookup = """
query($threadId: ID!) {
  node(id: $threadId) {
    ... on PullRequestReviewThread {
      id
      isResolved
      pullRequest { id headRefOid }
    }
  }
}
"""
    result = graphql(lookup, {"threadId": thread_id})
    thread = result.get("data", {}).get("node")
    if not isinstance(thread, dict) or thread.get("id") != thread_id:
        raise ReviewCtlError("review thread was not found")
    if thread.get("pullRequest", {}).get("id") != identity["id"]:
        raise ReviewCtlError("review thread does not belong to the guarded pull request")
    if thread.get("isResolved"):
        return thread

    mutation = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread { id isResolved pullRequest { id headRefOid } }
  }
}
"""
    result = graphql(mutation, {"threadId": thread_id})
    return result["data"]["resolveReviewThread"]["thread"]


def submit_review(
    repo: str,
    pr: int,
    expected_head: str,
    review_id: str,
    event: str,
    body: str,
) -> dict[str, Any]:
    require_head(repo, pr, expected_head)
    if event not in {"COMMENT", "REQUEST_CHANGES", "APPROVE"}:
        raise ReviewCtlError(f"unsupported review event: {event}")
    query = """
mutation($reviewId: ID!, $event: PullRequestReviewEvent!, $body: String!) {
  submitPullRequestReview(input: {
    pullRequestReviewId: $reviewId,
    event: $event,
    body: $body
  }) {
    pullRequestReview { id state submittedAt commit { oid } }
  }
}
"""
    result = graphql(
        query,
        {"reviewId": review_id, "event": event, "body": body},
    )
    return result["data"]["submitPullRequestReview"]["pullRequestReview"]


def mark_ready(repo: str, pr: int, expected_head: str) -> dict[str, Any]:
    identity = require_head(repo, pr, expected_head)
    if not identity.get("isDraft"):
        return identity
    query = """
mutation($pullRequestId: ID!) {
  markPullRequestReadyForReview(input: {pullRequestId: $pullRequestId}) {
    pullRequest { id headRefOid isDraft }
  }
}
"""
    result = graphql(query, {"pullRequestId": identity["id"]})
    return result["data"]["markPullRequestReadyForReview"]["pullRequest"]


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    def common(command: argparse.ArgumentParser) -> None:
        command.add_argument("--repo", required=True, help="OWNER/REPO")
        command.add_argument("--pr", required=True, type=int)
        command.add_argument("--expected-head", required=True)

    identity = sub.add_parser("identity", help="Read current PR identity")
    identity.add_argument("--repo", required=True)
    identity.add_argument("--pr", required=True, type=int)

    pending = sub.add_parser("create-pending", help="Create a pending review")
    common(pending)

    viewed = sub.add_parser("mark-viewed", help="Mark one reviewed file Viewed")
    common(viewed)
    viewed.add_argument("--path", required=True)

    comment = sub.add_parser("add-comment", help="Add a thread to a pending review")
    common(comment)
    comment.add_argument("--review-id", required=True)
    comment.add_argument("--path", required=True)
    comment.add_argument("--body", required=True)
    comment.add_argument("--subject-type", choices=("LINE", "FILE"), default="LINE")
    comment.add_argument("--line", type=int)
    comment.add_argument("--side", choices=("LEFT", "RIGHT"))
    comment.add_argument("--start-line", type=int)
    comment.add_argument("--start-side", choices=("LEFT", "RIGHT"))

    resolve = sub.add_parser(
        "resolve-thread", help="Resolve one verified review conversation"
    )
    common(resolve)
    resolve.add_argument("--thread-id", required=True)

    submit = sub.add_parser("submit", help="Submit a pending review")
    common(submit)
    submit.add_argument("--review-id", required=True)
    submit.add_argument(
        "--event", required=True, choices=("COMMENT", "REQUEST_CHANGES", "APPROVE")
    )
    submit.add_argument("--body", required=True)

    ready = sub.add_parser("mark-ready", help="Mark a reviewed Draft PR Ready")
    common(ready)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        ensure_auth()
        if args.command == "identity":
            result = pr_identity(args.repo, args.pr)
        elif args.command == "create-pending":
            result = create_pending(args.repo, args.pr, args.expected_head)
        elif args.command == "mark-viewed":
            result = mark_viewed(args.repo, args.pr, args.expected_head, args.path)
        elif args.command == "add-comment":
            result = add_comment(
                args.repo,
                args.pr,
                args.expected_head,
                args.review_id,
                args.path,
                args.body,
                args.subject_type,
                args.line,
                args.side,
                args.start_line,
                args.start_side,
            )
        elif args.command == "resolve-thread":
            result = resolve_thread(
                args.repo,
                args.pr,
                args.expected_head,
                args.thread_id,
            )
        elif args.command == "submit":
            result = submit_review(
                args.repo,
                args.pr,
                args.expected_head,
                args.review_id,
                args.event,
                args.body,
            )
        elif args.command == "mark-ready":
            result = mark_ready(args.repo, args.pr, args.expected_head)
        else:  # pragma: no cover - argparse guarantees this branch is unreachable.
            raise ReviewCtlError(f"unknown command: {args.command}")
    except ReviewCtlError as exc:
        print(f"reviewctl: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

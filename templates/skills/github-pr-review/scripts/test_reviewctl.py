from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import textwrap
import unittest
from unittest.mock import patch


SCRIPT_PATH = pathlib.Path(__file__).with_name("reviewctl.py")
SPEC = importlib.util.spec_from_file_location("reviewctl", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
reviewctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewctl)


class ReviewCtlTests(unittest.TestCase):
    def fake_gh(self, body: str) -> str:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        executable = pathlib.Path(temp_dir.name) / "gh"
        executable.write_text(
            "#!/usr/bin/env python3\n" + textwrap.dedent(body), encoding="utf-8"
        )
        executable.chmod(0o755)
        return str(executable)

    def test_create_pending_resumes_review_at_same_head(self) -> None:
        fake_gh = self.fake_gh(
            """
            import json
            import sys

            args = sys.argv[1:]
            if args[:2] == ["auth", "status"]:
                if "--json" in args:
                    print(json.dumps({"hosts": {}}))
                raise SystemExit(0)
            if args[:2] == ["pr", "view"]:
                print(json.dumps({
                    "id": "PR_1",
                    "headRefOid": "abc",
                    "url": "https://github.com/owner/repo/pull/7",
                    "author": {"login": "author"},
                    "isDraft": False,
                    "state": "OPEN",
                }))
                raise SystemExit(0)
            if args[:2] == ["api", "graphql"]:
                query = next(arg for arg in args if arg.startswith("query="))
                if "reviews" in query and "viewer" in query:
                    print(json.dumps({"data": {
                        "viewer": {"login": "reviewer"},
                        "repository": {"pullRequest": {"reviews": {
                            "nodes": [{
                                "id": "REVIEW_EXISTING",
                                "state": "PENDING",
                                "commit": {"oid": "abc"},
                                "author": {"login": "reviewer"},
                            }],
                            "pageInfo": {"hasNextPage": False},
                        }}},
                    }}))
                    raise SystemExit(0)
                print("duplicate pending review", file=sys.stderr)
                raise SystemExit(1)
            print("unexpected command", file=sys.stderr)
            raise SystemExit(99)
            """
        )
        stdout = io.StringIO()
        with patch.dict(reviewctl.os.environ, {"GH_BIN": fake_gh}), contextlib.redirect_stdout(
            stdout
        ):
            result = reviewctl.main(
                [
                    "create-pending",
                    "--repo",
                    "owner/repo",
                    "--pr",
                    "7",
                    "--expected-head",
                    "abc",
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(stdout.getvalue())["id"], "REVIEW_EXISTING")

    def test_invalid_credentials_fail_during_auth_preflight(self) -> None:
        fake_gh = self.fake_gh(
            """
            import json
            import sys

            args = sys.argv[1:]
            if args[:2] == ["auth", "status"]:
                if "--json" in args:
                    print(json.dumps({"hosts": {"github.com": [{
                        "active": True,
                        "state": "invalid",
                    }]}}))
                    raise SystemExit(0)
                print("authentication token is invalid", file=sys.stderr)
                raise SystemExit(1)
            print("unexpected command after auth preflight", file=sys.stderr)
            raise SystemExit(99)
            """
        )
        stderr = io.StringIO()
        with patch.dict(reviewctl.os.environ, {"GH_BIN": fake_gh}), contextlib.redirect_stderr(
            stderr
        ):
            result = reviewctl.main(["identity", "--repo", "owner/repo", "--pr", "7"])
        self.assertEqual(result, 2)
        self.assertIn("authentication token is invalid", stderr.getvalue())
        self.assertNotIn("unexpected command", stderr.getvalue())

    def test_gh_binary_accepts_explicit_override(self) -> None:
        with (
            patch.dict(reviewctl.os.environ, {"GH_BIN": "/custom/gh"}),
            patch.object(reviewctl.pathlib.Path, "is_file", return_value=True),
            patch.object(reviewctl.os, "access", return_value=True),
        ):
            self.assertEqual(reviewctl.gh_binary(), "/custom/gh")

    def test_head_change_blocks_write(self) -> None:
        with patch.object(
            reviewctl,
            "pr_identity",
            return_value={"id": "PR_1", "headRefOid": "new", "state": "OPEN"},
        ):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "HEAD changed"):
                reviewctl.require_head("owner/repo", 7, "old")

    def test_mark_viewed_uses_reviewed_path(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                return_value={
                    "data": {
                        "markFileAsViewed": {
                            "pullRequest": {"id": "PR_1", "headRefOid": "abc"}
                        }
                    }
                },
            ) as graphql,
        ):
            result = reviewctl.mark_viewed("owner/repo", 7, "abc", "src/app.py")
        self.assertEqual(result["headRefOid"], "abc")
        self.assertEqual(graphql.call_args.args[1]["path"], "src/app.py")

    def test_mark_ready_mutates_matching_draft_pr(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={
                    "id": "PR_1",
                    "headRefOid": "abc",
                    "isDraft": True,
                    "state": "OPEN",
                },
            ),
            patch.object(
                reviewctl,
                "graphql",
                return_value={
                    "data": {
                        "markPullRequestReadyForReview": {
                            "pullRequest": {
                                "id": "PR_1",
                                "headRefOid": "abc",
                                "isDraft": False,
                            }
                        }
                    }
                },
            ) as graphql,
        ):
            result = reviewctl.mark_ready("owner/repo", 7, "abc")
        self.assertFalse(result["isDraft"])
        self.assertIn("markPullRequestReadyForReview", graphql.call_args.args[0])
        self.assertEqual(graphql.call_args.args[1]["pullRequestId"], "PR_1")

    def test_mark_ready_is_idempotent_when_pr_is_already_ready(self) -> None:
        identity = {
            "id": "PR_1",
            "headRefOid": "abc",
            "isDraft": False,
            "state": "OPEN",
        }
        with (
            patch.object(reviewctl, "require_head", return_value=identity),
            patch.object(reviewctl, "graphql") as graphql,
        ):
            result = reviewctl.mark_ready("owner/repo", 7, "abc")
        self.assertEqual(result, identity)
        graphql.assert_not_called()

    def test_resolve_thread_mutates_matching_unresolved_thread(self) -> None:
        identity = {"id": "PR_1", "headRefOid": "abc", "state": "OPEN"}
        with (
            patch.object(reviewctl, "require_head", return_value=identity),
            patch.object(
                reviewctl,
                "graphql",
                side_effect=[
                    {
                        "data": {
                            "node": {
                                "id": "THREAD_1",
                                "isResolved": False,
                                "pullRequest": {"id": "PR_1", "headRefOid": "abc"},
                            }
                        }
                    },
                    {
                        "data": {
                            "resolveReviewThread": {
                                "thread": {
                                    "id": "THREAD_1",
                                    "isResolved": True,
                                    "pullRequest": {
                                        "id": "PR_1",
                                        "headRefOid": "abc",
                                    },
                                }
                            }
                        }
                    },
                ],
            ) as graphql,
        ):
            result = reviewctl.resolve_thread(
                "owner/repo", 7, "abc", "THREAD_1"
            )
        self.assertTrue(result["isResolved"])
        self.assertEqual(graphql.call_count, 2)
        self.assertIn("resolveReviewThread", graphql.call_args_list[1].args[0])

    def test_resolve_thread_is_idempotent_when_already_resolved(self) -> None:
        thread = {
            "id": "THREAD_1",
            "isResolved": True,
            "pullRequest": {"id": "PR_1", "headRefOid": "abc"},
        }
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                return_value={"data": {"node": thread}},
            ) as graphql,
        ):
            result = reviewctl.resolve_thread(
                "owner/repo", 7, "abc", "THREAD_1"
            )
        self.assertEqual(result, thread)
        self.assertEqual(graphql.call_count, 1)

    def test_resolve_thread_rejects_thread_from_another_pr(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                return_value={
                    "data": {
                        "node": {
                            "id": "THREAD_1",
                            "isResolved": False,
                            "pullRequest": {"id": "PR_2", "headRefOid": "abc"},
                        }
                    }
                },
            ),
        ):
            with self.assertRaisesRegex(
                reviewctl.ReviewCtlError, "does not belong"
            ):
                reviewctl.resolve_thread("owner/repo", 7, "abc", "THREAD_1")

    def test_resolve_thread_rejects_stale_lookup_head(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                return_value={
                    "data": {
                        "node": {
                            "id": "THREAD_1",
                            "isResolved": False,
                            "pullRequest": {"id": "PR_1", "headRefOid": "def"},
                        }
                    }
                },
            ) as graphql,
        ):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "HEAD changed"):
                reviewctl.resolve_thread("owner/repo", 7, "abc", "THREAD_1")
        self.assertEqual(graphql.call_count, 1)

    def test_resolve_thread_rejects_stale_mutation_head(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                side_effect=[
                    {
                        "data": {
                            "node": {
                                "id": "THREAD_1",
                                "isResolved": False,
                                "pullRequest": {"id": "PR_1", "headRefOid": "abc"},
                            }
                        }
                    },
                    {
                        "data": {
                            "resolveReviewThread": {
                                "thread": {
                                    "id": "THREAD_1",
                                    "isResolved": True,
                                    "pullRequest": {
                                        "id": "PR_1",
                                        "headRefOid": "def",
                                    },
                                }
                            }
                        }
                    },
                ],
            ),
        ):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "HEAD changed"):
                reviewctl.resolve_thread("owner/repo", 7, "abc", "THREAD_1")

    def test_resolve_thread_requires_confirmed_resolution(self) -> None:
        with (
            patch.object(
                reviewctl,
                "require_head",
                return_value={"id": "PR_1", "headRefOid": "abc", "state": "OPEN"},
            ),
            patch.object(
                reviewctl,
                "graphql",
                side_effect=[
                    {
                        "data": {
                            "node": {
                                "id": "THREAD_1",
                                "isResolved": False,
                                "pullRequest": {"id": "PR_1", "headRefOid": "abc"},
                            }
                        }
                    },
                    {
                        "data": {
                            "resolveReviewThread": {
                                "thread": {
                                    "id": "THREAD_1",
                                    "isResolved": False,
                                    "pullRequest": {
                                        "id": "PR_1",
                                        "headRefOid": "abc",
                                    },
                                }
                            }
                        }
                    },
                ],
            ),
        ):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "did not confirm"):
                reviewctl.resolve_thread("owner/repo", 7, "abc", "THREAD_1")

    def test_resolve_thread_rejects_changed_mutation_identity(self) -> None:
        invalid_threads = (
            {
                "id": "THREAD_2",
                "isResolved": True,
                "pullRequest": {"id": "PR_1", "headRefOid": "abc"},
            },
            {
                "id": "THREAD_1",
                "isResolved": True,
                "pullRequest": {"id": "PR_2", "headRefOid": "abc"},
            },
        )
        for invalid_thread in invalid_threads:
            with self.subTest(invalid_thread=invalid_thread):
                with (
                    patch.object(
                        reviewctl,
                        "require_head",
                        return_value={
                            "id": "PR_1",
                            "headRefOid": "abc",
                            "state": "OPEN",
                        },
                    ),
                    patch.object(
                        reviewctl,
                        "graphql",
                        side_effect=[
                            {
                                "data": {
                                    "node": {
                                        "id": "THREAD_1",
                                        "isResolved": False,
                                        "pullRequest": {
                                            "id": "PR_1",
                                            "headRefOid": "abc",
                                        },
                                    }
                                }
                            },
                            {
                                "data": {
                                    "resolveReviewThread": {
                                        "thread": invalid_thread
                                    }
                                }
                            },
                        ],
                    ),
                ):
                    with self.assertRaises(reviewctl.ReviewCtlError):
                        reviewctl.resolve_thread(
                            "owner/repo", 7, "abc", "THREAD_1"
                        )

    def test_parser_accepts_resolve_thread(self) -> None:
        args = reviewctl.parser().parse_args(
            [
                "resolve-thread",
                "--repo",
                "owner/repo",
                "--pr",
                "7",
                "--expected-head",
                "abc",
                "--thread-id",
                "THREAD_1",
            ]
        )
        self.assertEqual(args.command, "resolve-thread")
        self.assertEqual(args.thread_id, "THREAD_1")

    def test_line_comment_requires_line_and_side(self) -> None:
        with patch.object(reviewctl, "require_head"):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "require --line"):
                reviewctl.add_comment(
                    "owner/repo",
                    7,
                    "abc",
                    "REVIEW_1",
                    "src/app.py",
                    "finding",
                    "LINE",
                    None,
                    None,
                    None,
                    None,
                )

    def test_file_comment_rejects_line_arguments(self) -> None:
        with patch.object(reviewctl, "require_head"):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "must not include"):
                reviewctl.add_comment(
                    "owner/repo",
                    7,
                    "abc",
                    "REVIEW_1",
                    "src/app.py",
                    "finding",
                    "FILE",
                    4,
                    "RIGHT",
                    None,
                    None,
                )

    def test_submit_rejects_unknown_event(self) -> None:
        with patch.object(reviewctl, "require_head"):
            with self.assertRaisesRegex(reviewctl.ReviewCtlError, "unsupported"):
                reviewctl.submit_review(
                    "owner/repo", 7, "abc", "REVIEW_1", "MERGE", "summary"
                )


if __name__ == "__main__":
    unittest.main()

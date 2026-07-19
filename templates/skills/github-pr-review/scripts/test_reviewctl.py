from __future__ import annotations

import importlib.util
import pathlib
import unittest
from unittest.mock import patch


SCRIPT_PATH = pathlib.Path(__file__).with_name("reviewctl.py")
SPEC = importlib.util.spec_from_file_location("reviewctl", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
reviewctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewctl)


class ReviewCtlTests(unittest.TestCase):
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

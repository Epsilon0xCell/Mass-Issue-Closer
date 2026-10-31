import io
import subprocess
import sys
import types
import unittest
from unittest import mock

import main as closer


class FakeIssue:
    def __init__(self, number, title, is_pr=False):
        self.number = number
        self.title = title
        self.pull_request = object() if is_pr else None
        self.edits = []

    def edit(self, state=None):
        self.edits.append(state)


class FakeRepo:
    def __init__(self, issues):
        self._issues = issues

    def get_issues(self, state=None):
        assert state == "open"
        return list(self._issues)


class CloseIssuesTests(unittest.TestCase):
    def test_closes_issues_and_skips_pull_requests(self):
        issues = [FakeIssue(1, "bug"), FakeIssue(2, "pr", is_pr=True), FakeIssue(3, "typo")]
        out = io.StringIO()
        closed, skipped = closer.close_issues(FakeRepo(issues), out=out)
        self.assertEqual((closed, skipped), (2, 1))
        self.assertEqual(issues[0].edits, ["closed"])
        self.assertEqual(issues[1].edits, [])
        self.assertIn("Skipped pull request #2", out.getvalue())

    def test_dry_run_edits_nothing(self):
        issues = [FakeIssue(1, "bug")]
        out = io.StringIO()
        closed, _ = closer.close_issues(FakeRepo(issues), dry_run=True, out=out)
        self.assertEqual(closed, 1)
        self.assertEqual(issues[0].edits, [])
        self.assertIn("Would close issue #1", out.getvalue())


class MainTests(unittest.TestCase):
    def fake_github_module(self, repo):
        module = types.ModuleType("github")

        class FakeGithub:
            def __init__(self, pat):
                self.pat = pat

            def get_repo(self, name):
                return repo

        module.Github = FakeGithub
        return module

    def test_main_with_fake_github(self):
        repo = FakeRepo([FakeIssue(1, "bug")])
        with mock.patch.dict(sys.modules, {"github": self.fake_github_module(repo)}):
            self.assertEqual(closer.main(["dummy-pat", "owner/repo"]), 0)

    def test_api_failure_exits_1(self):
        module = types.ModuleType("github")

        class FailingGithub:
            def __init__(self, pat):
                pass

            def get_repo(self, name):
                raise RuntimeError("401 Bad credentials")

        module.Github = FailingGithub
        with mock.patch.dict(sys.modules, {"github": module}):
            self.assertEqual(closer.main(["dummy-pat", "owner/repo"]), 1)

    def test_bad_repo_shape_exits_2(self):
        self.assertEqual(closer.main(["dummy-pat", "no-slash"]), 2)


class HelpWithoutDependencyTests(unittest.TestCase):
    def test_help_works_without_pygithub_installed(self):
        # This environment has no PyGithub. Before the fix, --help
        # crashed on the top level import; it must print usage and
        # exit 0 now.
        out = subprocess.run(
            [sys.executable, "main.py", "--help"], capture_output=True, text=True
        )
        self.assertEqual(out.returncode, 0)
        self.assertIn("--dry-run", out.stdout)
        self.assertNotIn("ModuleNotFoundError", out.stderr)


if __name__ == "__main__":
    unittest.main()

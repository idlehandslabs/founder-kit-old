import os
import pathlib
import subprocess
import tempfile
import unittest

GUARD = pathlib.Path(__file__).parent / "guard.py"
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@users.noreply.github.com"]


def run(cwd, *args, env=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        run(self.tmp, "git", "init", "-q")
        (pathlib.Path(self.tmp) / "a.txt").write_text("hello\n")
        run(self.tmp, *GIT, "add", "-A")
        run(self.tmp, *GIT, "commit", "-qm", "base")

    def commit(self, name, text):
        path = pathlib.Path(self.tmp) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        run(self.tmp, *GIT, "add", "-A")
        run(self.tmp, *GIT, "commit", "-qm", "change")

    def guard(self, terms=""):
        env = {**os.environ, "PRIVATE_TERMS": terms}
        return run(self.tmp, "python3", str(GUARD), "HEAD~1", env=env)

    def test_clean_diff_passes(self):
        self.commit("b.txt", "nothing to see\n")
        self.assertEqual(self.guard().returncode, 0)

    def test_blocks_secret(self):
        # built by concatenation so this test file doesn't trip the guard itself
        self.commit("b.txt", "key = AKIA" + "ABCDEFGHIJKLMNOP\n")
        r = self.guard()
        self.assertEqual(r.returncode, 1)
        self.assertIn("AWS key", r.stdout)

    def test_blocks_email(self):
        self.commit("b.txt", "mail me: someone@" + "gmail.com\n")
        self.assertEqual(self.guard().returncode, 1)

    def test_blocks_private_term_without_printing_it(self):
        self.commit("b.txt", "lives in Springfield\n")
        r = self.guard("springfield")
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("springfield", r.stdout.lower())

    def test_blocks_protected_file(self):
        self.commit("agent/guard.py", "# weakened\n")
        self.assertEqual(self.guard().returncode, 1)


if __name__ == "__main__":
    unittest.main()

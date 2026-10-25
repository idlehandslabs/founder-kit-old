import pathlib
import shutil
import tempfile
import unittest

import init

HERE = pathlib.Path(__file__).parent


class InitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        shutil.copy(HERE / "CLAUDE.md", self.tmp / "CLAUDE.md")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_fills_every_placeholder(self):
        init.main(["--name", "Acme", "--budget", "50", "--root", str(self.tmp)])
        text = (self.tmp / "CLAUDE.md").read_text()
        self.assertNotIn("{{", text)
        self.assertIn("# Acme", text)
        self.assertIn("$50", text)

    def test_creates_state_and_keeps_existing(self):
        (self.tmp / "state").mkdir()
        (self.tmp / "state" / "LOG.md").write_text("mine")
        init.main(["--name", "Acme", "--root", str(self.tmp)])
        self.assertEqual((self.tmp / "state" / "LOG.md").read_text(), "mine")
        self.assertIn("Total: $100", (self.tmp / "state" / "BUDGET.md").read_text())
        self.assertTrue((self.tmp / "post-queue" / "published").is_dir())

    def test_rules_survive(self):
        init.main(["--name", "Acme", "--root", str(self.tmp)])
        text = (self.tmp / "CLAUDE.md").read_text()
        self.assertIn("NEVER post, publish, or send anything yourself", text)

    def test_bad_budget_rejected(self):
        with self.assertRaises(SystemExit):
            init.main(["--name", "A", "--budget", "1;rm", "--root", str(self.tmp)])


if __name__ == "__main__":
    unittest.main()

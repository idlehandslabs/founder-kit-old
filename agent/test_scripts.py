import pathlib
import re
import subprocess
import unittest

HERE = pathlib.Path(__file__).parent
PRIVATE = re.compile(r"shipcard|idle ?hands|roast|FF5A1F", re.I)


class KitScriptsTest(unittest.TestCase):
    def test_shell_scripts_parse(self):
        for sh in HERE.glob("*.sh"):
            r = subprocess.run(["bash", "-n", str(sh)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, f"{sh.name}: {r.stderr}")

    def test_capture_compiles(self):
        compile((HERE / "capture.py").read_text(), "capture.py", "exec")

    def test_no_company_specific_text(self):
        files = list(HERE.glob("*.sh")) + list(HERE.glob("*prompt.md")) + [HERE / "capture.py"]
        for f in files:
            self.assertIsNone(PRIVATE.search(f.read_text()), f.name)

    def test_prompts_keep_the_no_publish_rule(self):
        self.assertIn("DO NOT publish", (HERE / "cycle-prompt.md").read_text())
        self.assertIn("Do NOT publish", (HERE / "daily-article-prompt.md").read_text())


if __name__ == "__main__":
    unittest.main()

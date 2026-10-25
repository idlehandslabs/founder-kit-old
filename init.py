#!/usr/bin/env python3
"""Fill the {{PLACEHOLDERS}} in the kit's CLAUDE.md and create empty state/ skeletons."""
import argparse
import pathlib
import re
import sys

STATE_FILES = {
    "PRODUCT.md": "# Product\n\n(Not chosen yet. Cycle 1: decide, and explain why.)\n",
    "STATE.md": "# Current State\n\n## Needs human\n- Nothing yet.\n",
    "TASKS.md": "# Backlog\n\n- [ ] Cycle 1: choose the product.\n",
    "LOG.md": "# Run log\n",
    "JOURNAL.md": "# Founder's journal\n",
    "ATTEMPTS.md": "# Attempts (tried / result / why / next)\n",
    "BUDGET.md": "# Budget\n\nTotal: ${budget}\nSpent: $0\n\n| Date | Item | Cost | Approved |\n|---|---|---|---|\n",
    "METRICS.md": "# Metrics\n\n(Nothing collected yet.)\n",
}


def fill(text, values):
    for key, val in values.items():
        text = text.replace("{{%s}}" % key, val)
    return text


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--idea", default="choose one and justify it in state/PRODUCT.md")
    ap.add_argument("--budget", default="100")
    ap.add_argument("--voice", default="plain, honest, a little funny, no hype")
    ap.add_argument("--goal", default="first real user, then first dollar")
    ap.add_argument("--root", default=str(pathlib.Path(__file__).parent))
    a = ap.parse_args(argv)
    if not re.fullmatch(r"[0-9]+", a.budget):
        sys.exit("--budget must be a whole number")
    root = pathlib.Path(a.root)
    values = {"COMPANY_NAME": a.name, "PRODUCT_IDEA": a.idea, "BUDGET": a.budget,
              "VOICE": a.voice, "GOAL": a.goal}
    manual = root / "CLAUDE.md"
    manual.write_text(fill(manual.read_text(), values))
    state = root / "state"
    state.mkdir(exist_ok=True)
    for name, body in STATE_FILES.items():
        p = state / name
        if not p.exists():
            p.write_text(body.replace("{budget}", a.budget))
    for d in ("post-queue/published", "daily-log", "app"):
        (root / d).mkdir(parents=True, exist_ok=True)
        keep = root / d / ".gitkeep"
        if not keep.exists():
            keep.write_text("")


if __name__ == "__main__":
    main()

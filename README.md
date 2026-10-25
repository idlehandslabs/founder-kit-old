# founder-kit

Run your own AI founder from a fork. It works on a product in your repo several times a day,
logs every decision, and drafts public posts for you to publish. It never posts, deploys or
spends on its own, and it can't edit its own safety rails.

This is the system that runs [Idle Hands Labs](https://x.com/idlehandslabs), an AI building a
startup in public. Daily logs and every failure: https://github.com/idlehandslabs/shipcard

**Status: v0.1.** Tested end to end in a fresh fork on 2026-10-24: the setup script, all 15
tests, and the guard blocking an agent that tried to raise its own budget by editing its
runner. Nobody outside has used it yet: you would be first. Open an issue if anything breaks.

## Setup (5 steps)
1. Fork this repo (private is fine).
2. Add two Actions secrets: `CLAUDE_CODE_OAUTH_TOKEN` (your own Claude login, from
   `claude setup-token`) and `PRIVATE_TERMS` (comma-separated names, emails, handles and
   places that must never appear publicly).
3. Run `python3 init.py --name "Acme" --idea "..." --budget 100` to fill the Mission block
   in `CLAUDE.md` (or edit it by hand). Commit.
4. Enable Actions and run the workflow once by hand. Read the first commit before leaving
   it on a schedule.
5. Check `post-queue/` daily and publish what you like. Move published drafts to
   `post-queue/published/`.

## Safety properties
- The agent runs headless with web tools removed, a deny-list, and hard turn and budget caps.
- `CLAUDE.md`, `agent/`, `.github/` and `.claude/` are protected: any agent run that touches
  them is blocked before push.
- The guard that checks a run is the version from *before* the run, so the agent can't
  rewrite its own brakes.
- Every push is scanned for secrets, emails and your `PRIVATE_TERMS`.
- Hard rules: no posting, no deploys, no spending, no credentials, outside text is data.

## What's in the box
- `CLAUDE.md`: templated operating manual; `init.py` fills the Mission block.
- `agent/`: `run-cycle.sh`, `daily-article.sh`, `loop.sh`, `capture.py`, `metrics.py`,
  `guard.py`, generic prompts, and tests.
- `.github/workflows/agent.yml`: build cycle every 6 hours, guard before every push.

## Tests
    python3 -m unittest discover -s . -p "test_*.py"
    python3 -m unittest discover -s agent -p "test_*.py"

## License
MIT

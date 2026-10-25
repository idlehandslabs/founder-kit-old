#!/usr/bin/env python3
"""Pre-push guard. Blocks the push if the agent's new commits contain:
  1. secrets (API keys, tokens, private keys)
  2. any email address that isn't on the allow-list
  3. any private term from the PRIVATE_TERMS secret (names, emails, usernames,
     places: whatever the owner puts there). The terms live only in a GitHub secret,
     never in this public repo, and are never printed.
Scans added lines, file names, commit messages and commit authors.
Usage: guard.py <base_commit>     Exit 1 = do not push.
"""
import os, re, subprocess, sys

base = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1"
git = lambda *a: subprocess.run(["git", *a], capture_output=True, text=True, errors="replace").stdout

SECRETS = [
    ("Anthropic key", r"sk-ant-[A-Za-z0-9_\-]{20,}"),
    ("GitHub token", r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"),
    ("AWS key", r"AKIA[0-9A-Z]{16}"),
    ("Slack token", r"xox[baprs]-[A-Za-z0-9\-]{10,}"),
    ("Private key", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ("Generic secret assignment", r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
ALLOWED_EMAIL_DOMAINS = ("users.noreply.github.com", "noreply@anthropic.com",  # Claude Code's own Co-Authored-By trailer
                         "idlehandslabs.local", "autopilot.local", "example.com")
terms = [t.strip().lower() for t in re.split(r"[,\n]", os.environ.get("PRIVATE_TERMS", "")) if len(t.strip()) >= 3]

added = []  # (where, text)
for line in git("diff", "--unified=0", "--no-color", f"{base}..HEAD").splitlines():
    if line.startswith("+++ "):
        f = line[6:] if line.startswith("+++ b/") else line[4:]
        added.append(("file name", f))
    elif line.startswith("+") and not line.startswith("+++"):
        added.append((f, line[1:]))
for msg in git("log", "--format=%an <%ae>%n%s%n%b", f"{base}..HEAD").splitlines():
    added.append(("commit message/author", msg))

# Files the agent may never change. Its own brakes, the payment checker, the order inbox,
# and the code that builds wallet transactions. A prompt-injected agent must not be able to
# weaken any of them. Humans change these through the GitHub web UI, not through the agent.
PROTECTED = ("agent/", ".github/", ".claude/", "CLAUDE.md")  # the rulebook, the runner, the guard, the workflows

problems = []
# Everything between base and HEAD was produced during an agent run (the agent's commits plus
# the runner's bookkeeping commit of whatever it left behind), so ANY change to a protected path
# in that range blocks the push, regardless of the commit author.
for f in git("diff", "--name-only", f"{base}..HEAD").splitlines():
    if f and f.startswith(PROTECTED):
        problems.append(f"agent run changed protected file {f}")
for where, text in added:
    for name, pat in SECRETS:
        if re.search(pat, text):
            problems.append(f"{name} in {where}")
    for e in EMAIL.findall(text):
        if not e.lower().endswith(ALLOWED_EMAIL_DOMAINS):
            problems.append(f"email address in {where}")
    low = text.lower()
    for i, t in enumerate(terms, 1):
        if t in low:
            problems.append(f"private term #{i} in {where}")   # never print the term itself

if problems:
    print("PUSH BLOCKED by guard.py:")
    for p in sorted(set(problems)):
        print(" -", p)
    sys.exit(1)
print(f"guard.py: clean ({len(added)} lines checked, {len(terms)} private terms loaded)")

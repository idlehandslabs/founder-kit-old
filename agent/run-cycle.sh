#!/usr/bin/env bash
# One autonomous work cycle. Invoked by loop.sh or a scheduler (cron/launchd).
# Safe to run manually to test: ./agent/run-cycle.sh
set -uo pipefail

# --- Resolve paths (works even under cron/launchd with a minimal environment) ---
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"   # native-install default
cd "$REPO_DIR"

# --- Auth: prefer the subscription token for unattended runs ---
# Set CLAUDE_CODE_OAUTH_TOKEN in the environment (see README "Auth").
# An exported ANTHROPIC_API_KEY would override the subscription token, so drop it:
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then unset ANTHROPIC_API_KEY || true; fi

# --- Prevent overlapping cycles ---
exec 9>"$REPO_DIR/.cycle.lock"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ)  cycle already running — skipping" >> state/LOG.md
  exit 0
fi

mkdir -p logs
# anonymous identity for every commit the agent makes
export GIT_AUTHOR_NAME="ai-founder" GIT_AUTHOR_EMAIL="founder@users.noreply.github.com"
export GIT_COMMITTER_NAME="ai-founder" GIT_COMMITTER_EMAIL="founder@users.noreply.github.com"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# --- Run one cycle, fully non-interactive ---
# --permission-mode bypassPermissions : run non-interactively. 'dontAsk' reliably
#                              denies the agent's normal CHAINED shell commands
#                              (e.g. "git status | head; python3 --version"), which
#                              stalls every cycle. So we bypass prompts and rely on
#                              defense-in-depth instead: the deny-list in
#                              .claude/settings.json, the hard rules in CLAUDE.md, and
#                              keeping this repo an isolated folder. Run it somewhere you
#                              are comfortable letting an agent run shell commands freely
#                              (ideally the repo's own folder / a VM, not your whole disk).
# --disallowedTools           : removes web tools from the agent entirely.
# --max-turns / --max-budget : hard caps so a single cycle can't run away
set +e
"$CLAUDE_BIN" -p "$(cat agent/cycle-prompt.md)" \
  --output-format json \
  --permission-mode bypassPermissions \
  --allowedTools "Read" "Edit" "Write" "Glob" "Grep" "Bash" \
  --disallowedTools "WebFetch" "WebSearch" \
  --max-turns 30 \
  --max-budget-usd 0.60 \
  > "logs/cycle-$STAMP.json" 2> "logs/cycle-$STAMP.err"
RC=$?
set -e 2>/dev/null || true

# --- Truth recorder: log blocked actions / errors independently of the agent ---
python3 agent/capture.py "logs/cycle-$STAMP.json" cycle "$RC" >/dev/null 2>&1 || true

# --- Summarize into the human-readable log ---
COST="?"
if command -v jq >/dev/null 2>&1 && [ -s "logs/cycle-$STAMP.json" ]; then
  COST="$(jq -r '.total_cost_usd // "?"' "logs/cycle-$STAMP.json" 2>/dev/null || echo "?")"
fi
echo "$(date -u +%FT%TZ)  cycle rc=$RC cost=\$$COST  log=logs/cycle-$STAMP.json" >> state/LOG.md

# --- Make failures visible in CI (the raw logs are gitignored) ---
if [ "$RC" -ne 0 ]; then
  echo "Claude exited with code $RC. Last lines of its output:"
  tail -c 1500 "logs/cycle-$STAMP.json" 2>/dev/null; echo
  tail -c 1500 "logs/cycle-$STAMP.err" 2>/dev/null; echo
  echo "::error title=Cycle failed::Claude exited with code $RC. See state/ATTEMPTS.md for the reason."
fi

exit 0

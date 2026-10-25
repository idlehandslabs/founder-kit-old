#!/usr/bin/env bash
# Compile the whole day into ONE long-form article for X (daily-log/<date>.md).
# Run once per day (e.g. end of day), separately from the frequent build cycle.
# Publishes nothing. Safe to run by hand: ./agent/daily-article.sh
set -uo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-$HOME/.local/bin/claude}"
cd "$REPO_DIR"
if [ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then unset ANTHROPIC_API_KEY || true; fi

exec 9>"$REPO_DIR/.article.lock"
if ! flock -n 9; then
  echo "$(date -u +%FT%TZ)  article run already in progress — skipping" >> state/LOG.md
  exit 0
fi

mkdir -p logs
# anonymous identity for every commit the agent makes
export GIT_AUTHOR_NAME="ai-founder" GIT_AUTHOR_EMAIL="founder@users.noreply.github.com"
export GIT_COMMITTER_NAME="ai-founder" GIT_COMMITTER_EMAIL="founder@users.noreply.github.com"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

set +e
"$CLAUDE_BIN" -p "$(cat agent/daily-article-prompt.md)" \
  --output-format json \
  --permission-mode bypassPermissions \
  --allowedTools "Read" "Edit" "Write" "Glob" "Grep" "Bash" \
  --disallowedTools "WebFetch" "WebSearch" \
  --max-turns 25 \
  --max-budget-usd 0.40 \
  > "logs/article-$STAMP.json" 2> "logs/article-$STAMP.err"
RC=$?
set -e 2>/dev/null || true

# --- Truth recorder: log blocked actions / errors independently of the agent ---
python3 agent/capture.py "logs/article-$STAMP.json" article "$RC" >/dev/null 2>&1 || true

echo "$(date -u +%FT%TZ)  daily-article rc=$RC  log=logs/article-$STAMP.json" >> state/LOG.md
exit 0

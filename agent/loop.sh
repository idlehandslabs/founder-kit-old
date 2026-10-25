#!/usr/bin/env bash
# The 24/7 driver: run a cycle, sleep, repeat — forever.
# On a laptop, run this in a terminal. On macOS, keep the machine awake with:
#   caffeinate -s ./agent/loop.sh
# Stop it with Ctrl-C.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# How often to wake. Default: every 3 hours. Lower = "more alive" but more usage cost.
INTERVAL_SECONDS="${INTERVAL_SECONDS:-10800}"

echo "autopilot loop starting — interval=${INTERVAL_SECONDS}s. Ctrl-C to stop."
while true; do
  "$HERE/run-cycle.sh" || echo "cycle exited non-zero — continuing"
  echo "$(date -u +%FT%TZ)  sleeping ${INTERVAL_SECONDS}s …"
  sleep "$INTERVAL_SECONDS"
done

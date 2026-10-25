#!/usr/bin/env python3
"""Truth recorder: after each run, log what actually happened, independent of the agent.

Reads the run's JSON record (from `claude -p --output-format json`) and appends an
`auto` entry to state/ATTEMPTS.md: blocked commands, errors, turns, cost.
Usage: capture.py <run.json> <kind> <exit_code>
"""
import json, sys, datetime, pathlib

path, kind, rc = sys.argv[1], sys.argv[2], int(sys.argv[3])
log = pathlib.Path(__file__).resolve().parent.parent / "state" / "ATTEMPTS.md"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")

try:
    d = json.loads(pathlib.Path(path).read_text() or "{}")
except Exception as e:  # the run didn't even produce a record
    d = {"is_error": True, "result": f"no readable run record ({e})"}

denials = d.get("permission_denials") or []
errored = bool(d.get("is_error")) or rc != 0
cost = d.get("total_cost_usd")
turns = d.get("num_turns")

lines = [f"\n## {now} · auto ({kind})"]
if errored:
    reason = (d.get("result") or d.get("subtype") or "unknown error").strip().splitlines()[0][:300]
    lines.append(f"- **Run failed** (exit {rc}): {reason}")
for den in denials[:10]:
    cmd = (den.get("tool_input") or {}).get("command") or json.dumps(den.get("tool_input"))[:200]
    lines.append(f"- **Blocked by a guardrail:** `{den.get('tool_name')}` → `{str(cmd)[:200]}`")
if not errored and not denials:
    lines.append("- Run completed with no blocked actions or errors.")
lines.append(f"- Turns: {turns if turns is not None else '?'}"
             + (f" · Claude cost: ${cost:.2f} (not counted in the $100 budget)" if isinstance(cost, (int, float)) else ""))

with log.open("a") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))

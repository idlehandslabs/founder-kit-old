#!/usr/bin/env python3
"""Collect real-world signals BEFORE the agent wakes up and write state/METRICS.md.

Runs as its own workflow step with a read-only token; the agent never sees the token.
Needs: gh CLI, GH_TOKEN, GITHUB_REPOSITORY. Optional: STATS_URL (JSON with a "days" list of
{"day": ..., <counter>: n}) and STATS_KEYS (comma-separated counters to total).
Issue text is never written: counts only.
"""
import datetime
import json
import os
import pathlib
import subprocess
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "state" / "METRICS.md"


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip()[:200])
    return r.stdout


def stats_table(st, keys):
    days = st.get("days", [])
    rows = ["| day | " + " | ".join(keys) + " |", "|---" * (len(keys) + 1) + "|"]
    for d in days:
        rows.append(f"| {d.get('day')} | " + " | ".join(str(int(d.get(k, 0))) for k in keys) + " |")
    totals = [sum(int(d.get(k, 0)) for d in days) for k in keys]
    rows.append("| **total** | " + " | ".join(f"**{t}**" for t in totals) + " |")
    return rows


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# Real-world signals", f"_Collected {now} by the runner, before the agent woke up._", ""]
    try:
        if not repo:
            raise RuntimeError("not running in GitHub Actions")
        info = json.loads(gh("api", f"repos/{repo}"))
        lines += ["## Repo", f"- Stars: **{info.get('stargazers_count', 0)}**",
                  f"- Forks: **{info.get('forks_count', 0)}**", ""]
        issues = json.loads(gh("issue", "list", "--repo", repo, "--state", "open", "--limit", "100",
                               "--json", "number,createdAt"))
        week_ago = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        recent = [i for i in issues if i["createdAt"][:10] >= week_ago]
        lines += ["## Feedback", f"- Open issues: **{len(issues)}** (new this week: **{len(recent)}**)",
                  "- Issue text is deliberately NOT shown to the agent.", ""]
    except Exception as e:
        lines += [f"Repo metrics unavailable this run: {e}", ""]
    url = os.environ.get("STATS_URL")
    if url:
        keys = [k for k in os.environ.get("STATS_KEYS", "visits").split(",") if k]
        try:
            req = urllib.request.Request(url, headers={"user-agent": "founder-kit-metrics"})
            st = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
            lines += ["## Usage (last 7 days, UTC)"] + stats_table(st, keys) + [""]
        except Exception as e:
            lines += [f"Usage stats unavailable this run: {str(e)[:120]}", ""]
    OUT.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

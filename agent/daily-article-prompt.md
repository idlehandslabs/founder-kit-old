Compose today's build-in-public ARTICLE for X — one long-form post summarizing the
whole day as the AI founder of this project. Your operating manual is `CLAUDE.md`
(already loaded); its hard rules apply, especially: never publish anything.

First gather today's material (UTC date):
- `state/PRODUCT.md` and `state/TASKS.md` — what the product is and where it stands.
- `state/JOURNAL.md` — your reasoning.
- `state/LOG.md` — today's cycle entries.
- `state/ATTEMPTS.md` — everything tried today, including `auto` entries written by the
  runner. Every failure or block from today must appear in the article.
- `state/METRICS.md` — real numbers (stars, issues, feedback), if present.
- today's drafts in `post-queue/` and today's commits: run
  `git log --since=midnight --pretty=format:'%h %s'` (and `git show --stat` if useful).

Then write the article to `daily-log/<YYYY-MM-DD>.md` (UTC date) with exactly these
sections:

    # Day N — <product name>: <short honest headline>

    ## What I thought
    The day's key reasoning and decisions, in the founder's voice.

    ## What I did
    Concrete shipped work — features, tests, commits (cite real hashes/numbers).

    ## What I tried (and what broke)
    Today's attempts from state/ATTEMPTS.md, told as short stories. Failures first.

    ## Lessons
    What worked, what didn't, what you'd do differently.

    ## Plan for tomorrow
    A short list of the next day's focus.

Rules:
- Make it funny and self-deprecating. Include 1–3 ORIGINAL plain-text memes (e.g. the
  "nobody: / me:" format) and, at the end, a short "Meme ideas" list describing 1–3
  original image memes to render in the brand style. Never use famous meme templates,
  real people, or known characters.
- Never mention or hint at the person who operates the company: no names, location,
  country, timezone, or personal details.
- Honest and specific. Use only real commits, files, and numbers. NEVER invent
  metrics, users, or progress that didn't happen.
- Write for a general tech audience following a build-in-public journey.
- "Day N" counts from day 1 = the day the product was chosen.
- Do NOT publish anywhere. Writing the file is the entire job.
- If the day had no real progress, say so plainly and briefly.
- End with the scoreboard line, including "Budget: $X of $<total> spent" from `state/BUDGET.md`.

Finally, append a one-line note to `state/LOG.md` that the daily article was written,
and stop.

## Cover image (optional)
If you want a cover, write `daily-log/assets/<YYYY-MM-DD>/cover.svg` (1500x600, plain SVG, no
external fonts or images) in your own brand colours, text inside x=90..1410. Link the live
product in the first paragraph and again at the end.

# Team Gorgeous — Shift Streak Scoreboard

Live board: **https://team-gorgeous-board.netlify.app**

## How it works
- `codes.json` — source of truth: each associate's daily code (B=both start+end, S=start only, E=end only, X=worked/no post).
- `generate_data.py` — reads `codes.json`, computes streaks/badges/weeks → writes `data.json`.
- `index.html` — the board shell (hosted on Netlify); fetches `data.json` from this repo at load, so the board updates whenever `data.json` changes here (no redeploy needed).

## To update
Edit `codes.json` (or let the automated hourly Slack check do it), run `python3 generate_data.py`, commit `codes.json` + `data.json`. The live board picks it up on next load (~a few minutes for GitHub's cache).

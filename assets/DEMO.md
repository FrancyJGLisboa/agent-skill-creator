# Demo assets

This folder holds the README's visual demo. Two pieces:

- **`hero.svg`** — a static flow diagram (workflow description → 5-phase pipeline →
  17 platforms). Committed, renders on GitHub immediately, used as the fallback.
- **`demo.cast`** — an [asciinema](https://asciinema.org) v2 cast of the end-to-end
  flow (install → `/agent-skill-creator` → generated skill → run it). Render it to a
  GIF so the README shows motion.

## Render the GIF (one step — needs `agg`)

`agg` is the official asciinema GIF generator: <https://github.com/asciinema/agg>

```bash
# install agg (pick one)
brew install agg            # macOS
cargo install --git https://github.com/asciinema/agg

# render the committed cast to a GIF
agg --theme github-dark --font-size 22 assets/demo.cast assets/demo.gif
```

Commit `assets/demo.gif`, and the README's top visual will switch from the static
SVG to the animated GIF automatically (the README already points at `assets/demo.gif`
with the SVG as the `<img>` fallback).

## Re-record from scratch (optional)

The cast is hand-authored so it stays reproducible and small. To capture a **real**
session instead:

```bash
asciinema rec assets/demo.cast --overwrite --cols 90 --rows 26
# run: the bootstrap one-liner, then /agent-skill-creator "<your workflow>",
# then invoke the generated skill. Exit the shell to stop recording.
```

Keep it under ~15 seconds and end on the generated artifact — that beat is what
makes a cold visitor "get it".

## Storyboard (what the cast shows)

1. `curl … bootstrap.sh | sh` → "Detected Claude Code, Cursor, Gemini CLI / Installed".
2. `/agent-skill-creator "every Friday I clean the CRM export and email a regional
   sales report"` → Phases 1–5 stream by; validate / security / pipeline / evals all
   PASS.
3. `✓ weekly-crm-report-skill (12 files, evals, installer)` installed on 3 tools.
4. `/weekly-crm-report-skill data/crm-export.csv` → `report.pdf` + `dashboard.html`.
5. Tagline beat: "Same skill, same command, every tool."

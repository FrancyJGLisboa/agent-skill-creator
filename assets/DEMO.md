# Demo assets

This folder holds the README's visual demo. Two pieces:

- **`hero.svg`** — a static flow diagram (workflow description → 5-phase pipeline →
  17 platforms). Committed, renders on GitHub immediately, linked under the GIF as the
  conceptual overview / fallback.
- **`demo.cast`** — an [asciinema](https://asciinema.org) v2 cast that re-paces the
  **genuine output** of a generated skill's quality gates (`validate` → `security_scan`
  → eval `--rollout`). Rendered to `demo.gif`, the README's top visual.

## The honesty rule

Every line of output in `demo.cast` is **verbatim** real output captured from running the
commands below against the bundled example skill (`references/examples/weekly-crm-report`).
Nothing is hand-written or embellished. Only the `$ …` command prompts and an honest
`… (5 non-blocking warnings)` truncation marker are authored; the timing is paced for
readability (these are fast scripts that dump output near-instantly on a real TTY, so a
raw real-time capture would just flash). Re-running the commands reproduces the same output.

## Render the GIF (one step — needs `agg`)

`agg` is the official asciinema GIF generator: <https://github.com/asciinema/agg>

```bash
# install agg (pick one)
brew install agg            # macOS
cargo install --git https://github.com/asciinema/agg

# render the committed cast to a GIF (README defaults: small font, idle trimmed)
~/.claude/skills/readme-terminal-gif/scripts/render.sh assets/demo.cast assets/demo.gif
# or, plain agg:
agg --font-size 14 --idle-time-limit 2 --theme asciinema assets/demo.cast assets/demo.gif
```

## Re-build the cast from real output (reproducible)

The cast is built from the verbatim output of three real commands via the
`readme-terminal-gif` skill's replay path:

```bash
# 1. capture genuine output
python3 scripts/validate.py references/examples/weekly-crm-report          > /tmp/out_validate.txt 2>&1
python3 scripts/security_scan.py references/examples/weekly-crm-report      > /tmp/out_scan.txt 2>&1
python3 references/examples/weekly-crm-report/scripts/run_evals.py --rollout > /tmp/out_rollout.txt 2>&1

# 2. re-pace it into a cast (storyboard references those files; text stays verbatim)
~/.claude/skills/readme-terminal-gif/scripts/make_cast.py assets/storyboard.json --out assets/demo.cast

# 3. render + eyeball a frame before committing
~/.claude/skills/readme-terminal-gif/scripts/render.sh assets/demo.cast assets/demo.gif
~/.claude/skills/readme-terminal-gif/scripts/check_frame.py assets/demo.gif /tmp/frame.png 1.0
```

## Storyboard (what the cast shows)

A real quality-gate run on a generated skill, ending on the proof beat:

1. `$ validate.py …/weekly-crm-report` → **Status: VALID** (+ 5 non-blocking warnings, truncated).
2. `$ security_scan.py …/weekly-crm-report` → **Status: CLEAN — No security issues found.**
3. `$ run_evals.py --rollout` → 9 golden-case checks, all `pass` →
   **rollout: 9 passed, 0 failed, 0 errored.**

That closing line — a generated skill's bundled evals actually passing — is the beat that
makes a cold visitor "get it".

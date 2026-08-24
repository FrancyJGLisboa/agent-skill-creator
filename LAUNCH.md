# Launch playbook

A practical, honest guide to launching agent-skill-creator. Copy for each channel
is in [`docs/launch/`](docs/launch/).

## The honest part first

**Stars are a launch + virality outcome, not an engineering one.** A polished repo
is the *floor* — necessary, not sufficient. Repos that hit 10K stars in weeks almost
always have a **front-page moment**: Hacker News front page, a high-reach tweet, a
Product Hunt #1, or a big newsletter/creator pickup — sitting on top of a product
whose value is obvious in ~30 seconds.

This repo is now built to convert attention at a high rate (clear value above the
fold, a working visual, honest positioning, runnable examples, green CI). What it
cannot do by itself is *manufacture the attention*. That part is distribution, and
it's yours to drive. The single biggest lever is **one amplified push on a channel
where the value lands cold** — not incremental README tweaks.

Realistic framing: "10K in a month" requires a front-page hit **and** sustained
follow-through. Treat that as the stretch goal. The controllable goal is: ship a
launch good enough that *if* it gets seen, it converts — then maximize shots on goal.

## The conversion checklist

- [ ] First screen: tagline + working visual + one-liner install, no broken images.
- [ ] A 15-second demo (render `assets/demo.cast` → `assets/demo.gif`, see
      [`assets/DEMO.md`](assets/DEMO.md)) — **do this before launch; motion converts.**
- [ ] "Why this vs alternatives" table is visible and honest.
- [ ] ≥3 runnable examples a visitor can try in one command.
- [ ] CI badge is green on `main`.
- [ ] Repo description is current and topics are set on GitHub (see below).
- [ ] Tag matches the README version (`v6.1.0`).

## GitHub setup (do once, before launch)

- **Description:** "Turn existing work into validated agent skills with safe first-run
  verification, 17-platform installation, and governed GitHub Copilot team releases."
- **Topics:** `agent-skills`, `claude`, `claude-code`, `llm`, `ai-agents`,
  `developer-tools`, `cursor`, `copilot`, `cross-platform`, `mcp`.
- **Social preview image:** upload a PNG of `assets/hero.svg`
  (Settings → Social preview) so shared links render a card, not a generic icon.
- Pin the repo on your profile; enable Discussions.

Live repository check on 2026-08-24: GitHub Pages is enabled and points to
`https://francyjglisboa.github.io/agent-skill-creator/`; the repository has no
topics and Discussions is disabled. Treat those two settings as open actions, not
completed launch work. GitHub Pages updates after the documentation changes reach
`main`; editing `docs/index.html` locally does not publish the page.

## Sequencing (a sane order)

1. **T‑minus days:** render the demo GIF, set description/topics/social preview,
   confirm CI is green, tag `v6.1.0`. Line up 3–5 people who'll genuinely engage in
   the first hour (comments/upvotes from real users, not vote rings).
2. **Launch day, morning (US Pacific):** post **Show HN** (title options in
   [`docs/launch/show-hn.md`](docs/launch/show-hn.md)). HN rewards a plain, honest
   title and an author who answers every comment fast. Be present for 3–4 hours.
3. **Same morning:** fire the **tweet thread**
   ([`docs/launch/tweet-thread.md`](docs/launch/tweet-thread.md)) with the GIF; ask
   your network to amplify. Tag relevant accounts only where genuinely relevant.
4. **+1 day (if HN went well):** **Product Hunt**
   ([`docs/launch/product-hunt.md`](docs/launch/product-hunt.md)) and the targeted
   **subreddits** ([`docs/launch/reddit.md`](docs/launch/reddit.md)). Don't blast all
   channels at once — stagger so each gets a real first-hour push.
5. **Follow-through:** turn the best HN/Reddit questions into README FAQ entries and
   issues. Momentum compounds when newcomers see an active maintainer.

## What actually moves the needle (ranked)

1. **A demo that makes the value obvious in one glance.** Render the GIF.
2. **Showing up.** On HN/Reddit, fast, non-defensive author replies often matter
   more than the post itself.
3. **A title that states the value, not the cleverness.** "Show HN: Turn any
   workflow into an agent skill that installs on 17 AI tools" beats anything cute.
4. **One credible amplifier.** A single retweet from someone with reach in the
   Claude/agent space outperforms 50 cold posts.
5. **Proof it's real.** Runnable examples + green CI + honest limits → trust → stars.

## What to avoid

- Vote/star rings or asking for stars directly on HN — it backfires and risks bans.
- Overclaiming ("10x", "magic", inflated tool counts). The repo says **17
  platforms** because that's the real number; keep every claim true.
- Launching all channels simultaneously, or launching before the GIF exists.
- Going quiet after posting. Silence in the first hour kills threads.

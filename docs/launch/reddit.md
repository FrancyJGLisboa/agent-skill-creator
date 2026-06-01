# Reddit copy

Reddit punishes anything that smells like marketing. Post as a builder sharing a
tool, lead with the problem, disclose you're the author, and engage in comments.
Read each subreddit's self-promotion rules first; space posts out (don't blast all
the same day from one account).

## Where (ranked by fit)
- **r/ClaudeAI** — most on-target (Claude Code / skills audience).
- **r/ChatGPTCoding** — broad AI-coding tooling crowd.
- **r/LocalLLaMA** — tooling-savvy; lead with the cross-platform + determinism angle.
- **r/cursor**, **r/github_copilot** — niche but high-intent; frame per tool.

## Title options
- `I built a tool that turns a plain-English workflow into an agent skill that installs on 17 AI tools (Claude Code, Cursor, Copilot…)`
- `Tired of re-explaining workflows to Claude/Cursor every session — so I made a generator that writes the skill for you (open source)`

## Body
> I use Claude Code and Cursor daily and got tired of re-explaining the same
> workflows every session. Writing a proper agent skill by hand means learning the
> SKILL.md spec, getting activation right, writing the code, and testing it — a few
> hours each time.
>
> So I built **Agent Skill Creator** (MIT, open source). You describe what you do in
> plain English — or hand it a PDF / URL / script / transcript — and it runs a
> deterministic 5-phase pipeline and writes the whole skill: functional code, docs, a
> cross-platform installer for 17 tools, and its own **eval spec** (binary checks +
> golden cases) so the skill is a regression test from the start. `run_evals.py
> --rollout` actually runs the skill on the golden inputs and scores the real output.
>
> Honest about the limits in the README: it doesn't auto-grade subjective quality
> (those checks print as a checklist), the rollout is opt-in (runs arbitrary code),
> and it's not magic — a skill is only as good as the workflow you describe.
>
> Repo + runnable examples (try one in a single command):
> https://github.com/FrancyJGLisboa/agent-skill-creator
>
> I'm the author — happy to answer questions or take feature requests. What workflow
> would you want to turn into a skill first?

## Per-subreddit angle
- **r/ClaudeAI:** emphasize Claude Code skills + artifacts (charts) + the eval loop.
- **r/LocalLLaMA:** emphasize 17-platform reach, determinism (`run_pipeline.py`),
  stdlib-only tooling, no lock-in.
- **r/ChatGPTCoding:** emphasize "stop re-explaining workflows" + cross-tool install.
- **r/cursor / r/github_copilot:** open on that tool by name; note format adapters.

## Rules of engagement
- Always disclose you're the author (mods ban stealth promo).
- Reply to every top comment in the first hour.
- No cross-posting the identical text same-day; tailor the opener per sub.

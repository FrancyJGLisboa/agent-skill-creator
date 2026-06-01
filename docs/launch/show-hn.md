# Show HN copy

HN rewards plain, honest, specific. No marketing voice. Lead with what it does and
what's interesting/hard about it. Be in the thread to answer every comment fast.

## Title options (pick one; keep it factual)

1. `Show HN: Turn any workflow into an agent skill that installs on 17 AI tools`
2. `Show HN: Agent Skill Creator – describe a workflow, get a validated cross-platform skill`
3. `Show HN: Generate Claude/Cursor/Copilot agent skills from a plain-English workflow`

> HN strips emoji and punctuation games. Avoid "magic", "AI-powered", exclamation
> marks. The first title is the safest: concrete value + the surprising number.

## Body (first comment from the author)

> I kept re-explaining the same workflows to Claude Code / Cursor every session, and
> writing a proper agent skill by hand meant learning the SKILL.md spec, getting
> activation keywords right, writing the code, and testing it — a few hours each time.
>
> So I built a generator. You describe what you do in plain English (or hand it a
> PDF, a URL, a script, a transcript) and it runs a deterministic 5-phase pipeline:
> discovery → design (it derives binary eval criteria) → architecture → activation
> detection → build. The output is a complete skill with functional code, a bundled
> eval spec, a security scan, and a cross-platform installer that targets 17 tools
> (Claude Code, Cursor, Copilot, Gemini, Windsurf, Cline, Codex, …).
>
> Two things I think are interesting:
> - **Every generated skill ships its own metric.** It writes an eval spec (binary
>   checks + golden cases) and a runner, so the skill is a regression test from day
>   one — and `run_evals.py --rollout` actually runs the skill on the golden inputs
>   and scores the real output.
> - **Determinism over prose.** Multi-script skills get a single `run_pipeline.py`
>   orchestrator so an agent runs one command instead of sequencing steps from prose
>   it might misread.
>
> Honest limits: it doesn't auto-grade subjective "llm-judge" criteria (those print
> as a checklist), the eval rollout is opt-in (it runs arbitrary skill code), and a
> generated skill is only as good as the workflow you describe — it surfaces implicit
> requirements but it's not magic.
>
> Repo (MIT), runnable examples you can try in one command, CI green:
> https://github.com/FrancyJGLisboa/agent-skill-creator
>
> Happy to answer anything about the pipeline, the cross-platform install, or how the
> evals work.

## Comment-readiness (have answers ready)

- "Why not just Anthropic's skill-creator?" → it's great for interactive Claude
  authoring; this turns existing material into a validated skill that installs
  everywhere, with test/security gates. (Point to the comparison table.)
- "Does it lock me into Claude?" → no — 17 platforms, format adapters for Cursor
  (.mdc), Windsurf, Junie; universal `~/.agents/skills/` path.
- "How do I know the generated code isn't garbage?" → validate + security scan are
  hard gates; every skill ships an eval spec; show the example rollout output.
- "What does it cost / need?" → MIT, stdlib Python tooling, `git` + any one of 17
  tools; no API key to get started.

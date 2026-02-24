---
name: agent-skill-creator
description: This enhanced skill should be used when the user asks to create an agent, automate a repetitive workflow, create a custom skill, or needs advanced agent creation capabilities. Activates with phrases like every day, daily I have to, I need to repeat, create agent for, automate workflow, create skill for, need to automate, turn process into agent. Supports single agents, multi-agent suites, transcript processing, template-based creation, and interactive configuration. Claude will use the enhanced protocol to research APIs, define analyses, structure everything, implement functional code, and create complete skills autonomously with optional user guidance.
---
# Agent Creator - Meta-Skill

Teaches Claude Code how to autonomously create complete, production-ready agents as Claude Skills.

## When to Use

Activate when the user:
- Asks to create an agent: "Create an agent for [objective]"
- Asks to automate a workflow: "Every day I do [task], automate this"
- Asks to create a skill: "Create a skill for [domain]"
- Describes a repetitive process: "I repeatedly need to [task]"

## Creation Modes

| Mode | Trigger | Output |
|------|---------|--------|
| Single Agent | "Create an agent for X" | `./x-agent-cskill/` |
| Multi-Agent Suite | "Create a suite with N agents for..." | `./x-suite-cskill/` with N sub-skills |
| Transcript Processing | "Create agents from this transcript" | Extracts workflows, creates integrated suite |
| Template-Based | "Use the financial-analysis template" | Pre-configured structure, faster creation |
| Interactive | "Walk me through creating..." | Step-by-step wizard with preview |

## Architecture Decision

Choose skill type based on complexity:

- **Simple Skill** (single objective, <1000 lines): Single `SKILL.md` + scripts + references
- **Complex Skill Suite** (multiple workflows, >2000 lines): Multiple component skills with `.claude-plugin/marketplace.json`

All created skills use the `-cskill` suffix (e.g., `stock-analyzer-cskill/`).

## 6-Phase Autonomous Creation Protocol

### Phase 1: Discovery

**Goal**: Decide which API/data source to use.

1. Identify domain from user input (agriculture, finance, weather, etc.)
2. Research available APIs via `WebSearch` and `WebFetch`
3. Compare options on: data coverage, cost, rate limits, documentation quality
4. Select 1 API and document the decision with justification
5. Extract technical details: base URL, endpoints, auth, parameters, response format

**Output**: `DECISIONS.md` with API selection rationale. See `references/phase1-discovery.md`.

### Phase 2: Analysis Design

**Goal**: Define which analyses the agent will perform.

1. Brainstorm 10-15 typical user questions for the domain
2. Group by analysis type: simple queries, comparisons, rankings, trends, projections
3. Select 4-6 priority analyses covering 80% of use cases
4. For each: define name, inputs, outputs, methodology, and interpretation
5. Include a `comprehensive_{domain}_report()` function that combines all metrics into one call

**Output**: Analysis specifications. See `references/phase2-design.md`.

### Phase 3: Architecture

**Goal**: Structure the agent optimally.

1. Define folder structure based on complexity decision
2. Assign responsibilities per script file (fetch, parse, analyze, utils)
3. Plan reference files (API guide, methodologies, troubleshooting)
4. Define caching strategy and performance approach

Standard structure:
```
agent-name-cskill/
├── .claude-plugin/marketplace.json
├── SKILL.md
├── scripts/
│   ├── fetch_{domain}.py
│   ├── parse_{type}.py (one per data type)
│   ├── analyze_{domain}.py
│   └── utils/
│       ├── helpers.py
│       ├── cache_manager.py
│       └── validators/
├── references/
└── assets/
```

**Output**: Architecture plan. See `references/phase3-architecture.md`.

### Phase 4: Detection

**Goal**: Determine keywords for automatic activation.

1. List domain entities, metrics, and geographic terms
2. List action verbs: "query", "compare", "rank", "analyze", "forecast"
3. List question variations users might ask
4. Define negative scope (what should NOT activate this skill)
5. Create description (~200 words) with 60+ domain keywords

Implement 3-layer activation:
- **Layer 1**: 10-15 keyword phrases (exact match)
- **Layer 2**: 5-7 regex patterns (flexible match)
- **Layer 3**: Description for Claude NLU (fallback)

**Output**: Activation config. See `references/phase4-detection.md` and `references/activation-patterns-guide.md`.

### Phase 5: Implementation

**Goal**: Implement everything with real, functional code.

**Step 0 (MANDATORY)**: Create `.claude-plugin/marketplace.json` first. Validate JSON syntax before proceeding. Without this file, the skill cannot be installed.

```json
{
  "name": "agent-name",
  "plugins": [{
    "name": "agent-plugin",
    "description": "MUST match SKILL.md frontmatter description exactly",
    "source": "./",
    "skills": ["./"]
  }]
}
```

**Implementation order**:
1. Create directory structure
2. Write `SKILL.md` (frontmatter + when to use + workflows + examples). Sync description with marketplace.json
3. Implement utils first (`helpers.py`, `cache_manager.py`, validators)
4. Implement fetch script (1 method per API metric)
5. Implement parsers (1 parser per data type - see `references/phase5-implementation.md`)
6. Implement analysis functions (include `comprehensive_report`)
7. Write references with real content
8. Create README, DECISIONS.md, CHANGELOG.md

**Code quality requirements** (every script):
- Complete functions (no TODOs, no `pass`, no placeholders)
- Type hints on all functions
- Docstrings with Args/Returns/Raises/Example
- Error handling with logging
- `if __name__ == "__main__"` with argparse

See `references/quality-standards.md` for full checklist.

### Phase 6: Testing

**Goal**: Validate the created skill works correctly.

1. Generate unit tests for each script
2. Generate integration tests for the full pipeline
3. Test activation with 10+ sample queries
4. Validate marketplace.json installation
5. Run `tessl skill review` if available

See `references/phase6-testing.md` for test templates.

## Post-Creation: Cross-Platform Export

After creating a skill, optionally export for other Claude platforms:

```bash
python scripts/export_utils.py ./skill-name-cskill --variant desktop  # .zip for Claude Desktop
python scripts/export_utils.py ./skill-name-cskill --variant api      # .zip for Claude API
python scripts/export_utils.py ./skill-name-cskill                    # Both variants
```

See `references/export-guide.md` and `references/cross-platform-guide.md`.

## Agent Creation Checklist

Before considering the agent complete, verify:

- [ ] `.claude-plugin/marketplace.json` exists and is valid JSON
- [ ] `marketplace.json` description matches `SKILL.md` frontmatter description exactly
- [ ] `SKILL.md` has valid frontmatter with `name` and `description`
- [ ] All Python scripts run without errors
- [ ] No TODOs, placeholders, or `pass` statements in code
- [ ] All functions have type hints and docstrings
- [ ] Error handling covers API failures, invalid data, rate limits
- [ ] References contain real content (not just links)
- [ ] README has installation and usage instructions
- [ ] DECISIONS.md documents API selection rationale
- [ ] Tests cover core functionality
- [ ] Activation tested with 10+ sample queries

## Troubleshooting

**marketplace.json errors**:
- Missing file: Create `.claude-plugin/marketplace.json` before anything else
- Invalid JSON: Validate with `python3 -c "import json; json.load(open('path'))"`
- Description mismatch: Copy SKILL.md frontmatter description exactly to marketplace.json

**Skill not activating**: Check 3-layer activation config. Ensure description has 60+ domain keywords.

**API errors**: Verify API key, check rate limits, test endpoints manually first.

## Negative Scope

Do NOT activate for: general programming questions, debugging existing code, explaining concepts, file operations, git commands, or tasks that don't involve creating a new agent or skill.

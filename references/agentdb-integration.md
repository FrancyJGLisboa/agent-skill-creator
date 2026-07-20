# AgentDB Integration

> **STATUS: DESIGN DOCUMENT — NOT IMPLEMENTED.**
> Nothing described in this file exists in the codebase: there is no
> `integrations/` directory, no `agentdb_bridge.py`, no nightly learner, and no
> reflexion/causal/skill-extraction storage. The skill creator neither reads
> nor writes any AgentDB state today. This document is a design sketch for a
> possible future learning layer. The learning loop that DOES exist and ship
> with every generated skill is the eval harness: `run_evals.py` with baseline
> promotion, a regression gate, and a holdout split (see
> `phase2-eval-assessment.md`). Do not describe AgentDB features as current
> behavior in user-facing output.

## Overview

AgentDB is an invisible learning system that improves skill creation quality over time. It operates behind the scenes during every skill creation episode, recording decisions, outcomes, and patterns. The user never interacts with AgentDB directly -- they simply get progressively better skill outputs as the system accumulates experience.

**Key principle**: AgentDB is always optional. The skill creator works identically with or without AgentDB installed. When available, it provides enhanced intelligence. When absent, the system falls back to its standard pipeline with zero degradation.

## What AgentDB Does

AgentDB provides three learning mechanisms:

### Reflexion Memory

Stores complete creation episodes (what was attempted, what worked, what failed) and retrieves relevant past experiences when facing similar tasks.

- After creating a financial analysis skill, AgentDB remembers which API scored highest, which analysis patterns the user liked, and which configurations caused issues.
- The next time someone requests a financial skill, the system retrieves these episodes and uses them to make better Phase 1 and Phase 2 decisions.

### Causal Reasoning

Tracks cause-and-effect relationships between creation decisions and outcomes.

- "Using Alpha Vantage with rate limiting causes 23% fewer API errors than without"
- "Including a comprehensive report function causes 40% higher user satisfaction"
- These causal links accumulate over time and influence template selection and configuration defaults.

### Skill Extraction

Identifies reusable patterns from successful creations and stores them as transferable skills.

- A caching strategy that worked well for NOAA data gets extracted and applied to other API-heavy skills.
- A report generation pattern that received positive feedback gets promoted to a template default.

## Integration Points in the 5-Phase Pipeline

AgentDB hooks into each phase of the creation pipeline transparently.

### Phase 1: Discovery

**Without AgentDB**: System researches APIs via WebSearch, compares options, selects the highest-scoring candidate.

**With AgentDB**: Before researching, the system queries reflexion memory for past discovery episodes in the same domain. If a previous creation already evaluated NOAA vs. Open-Meteo for climate data, the system reuses that evaluation (with a freshness check) instead of repeating the research from scratch.

```
AgentDB query: "What APIs were selected for climate/weather domains?"
Result: NOAA selected 3 times (avg score 8.7/10), Open-Meteo selected 2 times (9.1/10)
Effect: Open-Meteo is pre-ranked higher, saving 5-10 minutes of research
```

### Phase 2: Design

**Without AgentDB**: System designs 4-6 analyses based on domain best practices and API capabilities.

**With AgentDB**: Causal reasoning identifies which analysis patterns have the highest success rates for the domain. Reflexion memory recalls which analyses users requested most frequently.

```
AgentDB query: "What analyses work best for financial skills?"
Result: Technical indicators (92% retention), sector comparison (87%),
        portfolio tracking (85%), news sentiment (61%)
Effect: News sentiment is deprioritized; technical indicators are designed first
```

### Phase 3: Architecture

**Without AgentDB**: System chooses simple vs. complex architecture based on scope.

**With AgentDB**: Historical data on suite sizes vs. maintainability informs the decision. If past suites with 4+ components had refactoring issues, the system might recommend splitting differently.

```
AgentDB query: "What architecture works best for 3-workflow skills?"
Result: Simple skill chosen 8/10 times, suite chosen 2/10. Simple had
        fewer maintenance issues (causal link: simple -> 30% less rework)
Effect: Simple skill recommended with higher confidence
```

### Phase 4: Detection

**Without AgentDB**: System generates description and keywords based on domain analysis.

**With AgentDB**: Extracted skills from past successful activations inform keyword selection. If "stock analysis" activated more reliably than "equity research" in past skills, the former is prioritized.

```
AgentDB query: "What keywords had highest activation rates for finance?"
Result: "stock analysis" (98%), "market data" (95%), "portfolio" (93%),
        "equity research" (72%), "securities" (68%)
Effect: High-activation keywords prioritized in description
```

### Phase 5: Implementation

**Without AgentDB**: System creates all files following the standard pipeline.

**With AgentDB**: Learned improvements from past creations are applied. If a specific error-handling pattern reduced runtime failures, it is included automatically. After creation, the episode is stored for future learning.

```
AgentDB action: Store episode
  - Domain: climate
  - Template used: climate-analysis
  - APIs: Open-Meteo + NOAA
  - Analyses: 5 implemented
  - Validation: passed (10/10)
  - Security: passed (clean)
  - User satisfaction: pending
```

## Learning Progression

AgentDB's value grows with usage. Here is what to expect at different stages.

### First Creation (No History)

- AgentDB has no past episodes to draw from
- Behavior is identical to running without AgentDB
- The creation episode is stored for future reference
- No noticeable difference in output quality

### After 5+ Creations

- Reflexion memory has enough episodes to identify domain patterns
- API selection benefits from past evaluations (fewer redundant searches)
- Common analysis patterns are recognized and reused
- Estimated time savings: 10-15% per creation

### After 10+ Creations

- Causal reasoning has enough data to identify reliable cause-effect links
- Template matching improves as keyword effectiveness data accumulates
- Architecture decisions are informed by maintenance outcomes
- Skill extraction produces reusable patterns across domains
- Estimated time savings: 20-30% per creation

### After 30+ Days of Usage

- Nightly learner has processed all episodes and extracted high-confidence patterns
- Cross-domain insights emerge (e.g., "caching improves all API-heavy skills by 25%")
- Template recommendations reach high accuracy (>90% user acceptance)
- The system begins suggesting proactive improvements to existing skills
- Estimated time savings: 30-40% per creation

## Graceful Fallback

AgentDB availability is checked once at initialization. If unavailable, the system operates in fallback mode with zero user-visible impact.

### Detection Order

1. Check for native `agentdb` CLI in PATH
2. Check for `npx @anthropic-ai/agentdb` availability
3. Attempt automatic installation via npm (if npm is available)
4. If all checks fail, enter fallback mode silently

### Fallback Behavior

| Feature | With AgentDB | Without AgentDB (Fallback) |
|---------|-------------|---------------------------|
| Phase 1 Discovery | Informed by past episodes | Full research from scratch |
| Phase 2 Design | Ranked by historical success | Standard domain analysis |
| Phase 3 Architecture | Data-driven recommendation | Heuristic-based recommendation |
| Phase 4 Detection | Keywords ranked by activation history | Keywords from domain analysis |
| Phase 5 Implementation | Learned patterns applied | Standard patterns applied |
| Episode storage | Saved for future learning | Not stored (nothing to store to) |
| Output quality | Progressively improving | Consistently good (baseline) |

### Error Tolerance

If AgentDB is available but encounters errors during operation:
- First 3 errors: Logged silently, operation retried with fallback
- After 3 errors: AgentDB is disabled for the remainder of the session
- Next session: AgentDB is re-initialized (errors do not persist across sessions)

No AgentDB error ever surfaces to the user or interrupts the creation pipeline.

## Privacy and Performance

### All Local

- AgentDB stores all data locally in `~/.agentdb/`
- No data is transmitted to external servers
- No telemetry, analytics, or usage tracking
- The user's creation history stays on their machine

### No External Dependencies at Runtime

- AgentDB is an npm package, but once installed it runs locally
- If npm is unavailable, AgentDB simply does not install (fallback mode)
- The skill creator itself has zero npm dependencies -- AgentDB is purely optional

### Performance Impact

| Operation | Without AgentDB | With AgentDB | Overhead |
|-----------|----------------|--------------|----------|
| Initialization | 0ms | 50-200ms (one-time check) | Negligible |
| Phase 1 query | N/A | 10-50ms | Negligible |
| Phase 5 store | N/A | 20-100ms | Negligible |
| Disk usage | 0 | 1-10 MB (grows with usage) | Minimal |

AgentDB operations are asynchronous where possible and never block the main creation pipeline.

## Technical Implementation

### Bridge Architecture

The integration uses a bridge pattern (`integrations/agentdb_bridge.py`) that isolates all AgentDB operations behind a clean interface:

```python
from integrations.agentdb_bridge import enhance_agent_creation

# Called internally during skill creation -- never by the user
intelligence = enhance_agent_creation(
    user_input="Create a climate analysis skill",
    domain="climate"
)

# intelligence.template_choice -> "climate-analysis" (or None in fallback)
# intelligence.success_probability -> 0.87 (or 0.0 in fallback)
# intelligence.learned_improvements -> ["Use Open-Meteo over NOAA for forecasts"]
```

### Module Functions

| Function | Purpose |
|----------|---------|
| `enhance_agent_creation(input, domain)` | Pre-creation intelligence gathering |
| `enhance_template(template, domain)` | Template improvement from learned patterns |
| `store_agent_experience(name, experience)` | Post-creation episode recording |
| `get_agent_learning_summary(name)` | Internal progress tracking |

### Configuration

AgentDB auto-configures on first use. The configuration lives at `~/.agentdb/config.json`:

```json
{
  "reflexion": {
    "auto_save": true,
    "compression": true
  },
  "causal": {
    "auto_track": true,
    "utility_model": "outcome_based"
  },
  "skills": {
    "auto_extract": true,
    "success_threshold": 0.8
  },
  "nightly_learner": {
    "enabled": true,
    "schedule": "2:00 AM"
  }
}
```

No user action is required to create or maintain this configuration. The bridge handles everything automatically.

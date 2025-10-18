# Agent Creator - Meta-Skill for Claude Code

**Meta-skill that teaches Claude Code to create complete agents with Claude Skills in a fully autonomous way!**

You describe a repetitive workflow → Claude creates a complete production-ready agent in 60-90 minutes.

---

## 🎯 What It Is and What It Does

### Problem It Solves

Creating a Claude Code agent manually is:
- ⏰ **Time-consuming**: 20-30 hours of work
- 🧠 **Complex**: Requires knowledge of APIs, Python, architecture
- 🔍 **Labor-intensive**: Research APIs, define analyses, structure, code, document

### Solution: Agent-Creator

**You do:**
```
"Automate this workflow: every day I download crop data,
compare current year vs previous, takes 2 hours."
```

**Claude Code does:**
1. 🔍 Research available APIs → Decide the best one
2. 🎨 Define useful analyses → Prioritize by value
3. 🏗️ Structure project → Optimal architecture
4. 💻 Implement Python code → Functional, no TODOs
5. 📝 Write documentation → 12,000+ words
6. ⚙️ Create configs → Real values
7. 📦 Deliver agent → Production-ready in subdirectory

**Result:** Complete agent in ~90 minutes!

---

## 🚀 Quick Installation

### Prerequisites

- Claude Code CLI installed
- Python 3.8+ (for agents that will be created)

### Step 1: Install in Claude Code

**In the Claude Code terminal**, run:

```bash
/plugin marketplace add FrancyJGLisboa/agent-creator-skill
```

### Step 2: Verify Installation

```bash
/plugin list
```

You should see:
```
✓ agent-creator
```

### Done! 🎉

The meta-skill is installed and ready to use.

---

## 💡 How to Use (Tutorial Guide)

### Basic Usage - Describe Your Workflow

**In Claude Code**, simply describe what you do repeatedly:

```
👤 You type:
"Automate this workflow: every day I download US crop data,
compare current year vs previous, rank states. Takes 2 hours."
```

**🤖 Claude Code:**
```
[Detects keyword: "automate"]
[Activates skill: agent-creator]
[Loads 5-phase protocol]

🔍 Phase 1: Researching US agriculture APIs...
   ✓ 5 options found
   ✓ Decided: USDA NASS QuickStats API
     Reason: Free, data since 1866, complete coverage

🎨 Phase 2: Defining analyses...
   ✓ 15 typical questions identified
   ✓ 5 main analyses: YoY, Ranking, Trends, Reports

🏗️ Phase 3: Structuring project...
   ✓ 3 scripts + 3 utils planned

🎯 Phase 4: Defining automatic detection...
   ✓ 50+ keywords identified

⚙️ Phase 5: Implementing code...
   ✓ SKILL.md (6,200 words)
   ✓ fetch_nass.py (280 lines)
   ✓ parse_nass.py (180 lines)
   ✓ analyze_nass.py (520 lines)
   ✓ utils/ (350 lines)
   ✓ references/ (5,000 words)
   ✓ .claude-plugin/marketplace.json ✅
   ✓ README.md (800 words)

✅ AGENT CREATED: ./usda-agriculture-agent/

🚀 To install:
/plugin marketplace add ./usda-agriculture-agent
```

### What You Get

A complete directory:

```
./usda-agriculture-agent/
├── .claude-plugin/
│   └── marketplace.json         ← For Claude Code installation
├── SKILL.md                     ← Complete orchestration (6,000 words)
├── scripts/
│   ├── fetch_nass.py           ← API client (280 lines)
│   ├── parse_nass.py           ← Parsing & validation (180 lines)
│   ├── analyze_nass.py         ← Analyses (520 lines)
│   └── utils/
│       ├── cache_manager.py    ← Smart cache
│       ├── rate_limiter.py     ← Rate limiting
│       └── validators.py       ← Validations
├── references/
│   ├── api-guide.md            ← How to use the API
│   ├── analysis-methods.md     ← Detailed methodologies
│   └── troubleshooting.md      ← Problem solving
├── assets/
│   ├── config.json             ← Real configurations
│   └── metadata.json           ← Metadata
├── DECISIONS.md                 ← Decision justifications
└── README.md                    ← Usage instructions
```

**Total:** ~2,000 lines of code + ~12,000 words of documentation

---

## 🔄 How It Works Internally (5 Phases)

### PHASE 1: Discovery (API Research)

**What it does:**
- Research available public APIs for the domain
- Uses `WebSearch` and `WebFetch` to find options
- Compares APIs by: coverage, cost, rate limits, quality
- **DECIDES** autonomously which to use

**Example (Agriculture):**
```bash
WebSearch: "US agriculture API free historical data"
WebSearch: "USDA API documentation"
WebFetch: https://quickstats.nass.usda.gov/api

→ DECISION: USDA NASS QuickStats API
  Justification: Free, data since 1866, all crops
```

---

### PHASE 2: Design (Analysis Definition)

**What it does:**
- Brainstorm 10-15 typical user questions
- Group by analysis type
- **DEFINES** 4-6 priority analyses
- Specifies methodologies (formulas, interpretations)

**Example:**
```
Typical questions:
- "Corn production in 2023?"
- "Compare soybeans 2024 vs 2023"
- "Top 10 producing states"

→ ANALYSES DEFINED:
  1. YoY Comparison (year vs year)
  2. State Ranking (top producers)
  3. Trend Analysis (trends)
  4. Report Generation (reports)
```

---

### PHASE 3: Architecture (Structuring)

**What it does:**
- Defines folder and file structure
- Specifies responsibilities of each script
- Plans cache strategy and performance

**Example:**
```
→ STRUCTURE:
  scripts/
    - fetch_nass.py (API requests)
    - parse_nass.py (parsing)
    - analyze_nass.py (analyses)
    utils/
      - cache_manager.py
      - rate_limiter.py
```

---

### PHASE 4: Detection (Automatic Activation)

**What it does:**
- Lists domain keywords
- Determines when skill should activate
- Creates optimized description

**Example:**
```
→ KEYWORDS:
  Entities: USDA, NASS, agriculture
  Commodities: corn, soybeans, wheat
  Metrics: production, area, yield
  Actions: compare, ranking, trend
```

---

### PHASE 5: Implementation (Complete Code)

**What it does:**
- Creates **marketplace.json** (REQUIRED!)
- Implements functional Python code
- Writes SKILL.md (5000+ words)
- Creates references with useful content
- Generates real configs

**Commands executed internally:**
```bash
mkdir -p agent-name/{scripts/utils,references,assets,.claude-plugin}
# Write: .claude-plugin/marketplace.json
# Write: SKILL.md
# Write: scripts/fetch_*.py
# Write: scripts/parse_*.py
# Write: scripts/analyze_*.py
# Write: utils/cache_manager.py
# Write: references/*.md
# Write: assets/*.json
# Write: README.md
```

---

## 📖 Practical Usage Examples

### Example 1: Agriculture (USDA)

**👤 Input in Claude Code:**
```
"Automate: every day I download US crop data,
compare current year vs previous, rank states.
Takes 2 hours."
```

**🤖 Claude executes (autonomously):**
```
Phase 1: Research → USDA NASS API
Phase 2: Define → YoY, Ranking, Trends
Phase 3: Structure → 3 scripts + 2 utils
Phase 4: Keywords → USDA, corn, soybeans, production
Phase 5: Implement → 1,410 lines of code

✅ Agent created: ./usda-agriculture-agent/
```

**💻 How to install the created agent:**
```bash
# In Claude Code
/plugin marketplace add ./usda-agriculture-agent
```

**🎯 How to use:**
```
"US corn production in 2023"
"Compare soybeans this year vs last year"
"Top 10 wheat producing states"
```

---

### Example 2: Finance (Stocks)

**👤 Input:**
```
"Need agent for stock analysis:
fetch prices, calculate RSI and MACD,
compare with benchmarks. Daily, 3h."
```

**🤖 Claude creates:**
```
Phase 1: Alpha Vantage API (or Yahoo Finance)
Phase 2: Price fetching, RSI, MACD, Benchmarking
Phase 3-5: Implement everything

✅ Created: ./stock-technical-analysis-agent/
```

**💻 Install:**
```bash
/plugin marketplace add ./stock-technical-analysis-agent
```

---

### Example 3: Climate (Real Case from Today!)

**👤 Input:**
```
"Create agent for climate analysis of Sorriso, Mato Grosso.
Need to analyze temperature and precipitation, historical trends."
```

**🤖 Claude executed (5 autonomous phases):**

```
🔍 PHASE 1: Climate API Research
   Researched: INMET, Open-Meteo, OpenWeather, Visual Crossing
   Compared: Coverage, cost, historical data
   ✓ DECIDED: Open-Meteo Historical Weather API
     • Free (no API key!)
     • Data since 1940 (84+ years)
     • ERA5 reanalysis (high quality)
     • REST API (easy integration)

🎨 PHASE 2: Analysis Design
   Brainstorm: 15 typical questions
   ✓ DEFINED: 6 main analyses
     1. Basic time series
     2. Temporal comparison (YoY)
     3. Trend analysis (CAGR, regression)
     4. Anomaly detection (Z-score)
     5. Seasonal analysis (monthly climatology)
     6. Descriptive statistics

🏗️ PHASE 3: Architecture
   ✓ STRUCTURED:
     scripts/
       - fetch_climate.py (320 lines)
       - parse_climate.py (180 lines)
       - analyze_climate.py (420 lines)
     utils/
       - cache_manager.py (350 lines)
       - validators.py (450 lines)
       - statistics.py (350 lines)
   ✓ Cache: Historical permanent, current year 24h
   ✓ Validations: Ranges, physical consistency, continuity

🎯 PHASE 4: Automatic Detection
   ✓ KEYWORDS: Sorriso, temperature, precipitation, rain, climate,
               trend, historical, anomaly, compare
   ✓ DESCRIPTION: 200 words optimized

⚙️ PHASE 5: Complete Implementation
   ✓ .claude-plugin/marketplace.json
   ✓ SKILL.md (6,800 words)
   ✓ Python scripts (2,070 lines)
   ✓ References (1,500 words)
   ✓ Configs (config.json, metadata.json)
   ✓ README.md + DECISIONS.md

✅ AGENT CREATED: ./climate-analysis-sorriso-mt/
```

**📊 Statistics:**
- **Code:** 2,070 lines of Python
- **Documentation:** 13,600 words
- **Files:** 16 main files
- **Time:** ~90 minutes of autonomous creation

**💻 Installation of created agent:**
```bash
# In terminal
cd climate-analysis-sorriso-mt
pip install -r requirements.txt

# In Claude Code
/plugin marketplace add ./climate-analysis-sorriso-mt
```

**🎯 Using the created agent:**
```
👤 "What's the average temperature in Sorriso over the last 10 years?"
🤖 [Skill activates automatically]
   [Fetches data from API]
   [Analyzes and responds]

👤 "Rain trend in Sorriso since 1990"
🤖 [34-year trend analysis]
   [Returns rate of change, significance, projection]
```

---

## 🔄 How It Works: The 5 Autonomous Phases

### PHASE 1: DISCOVERY (API Research)

**Objective:** DECIDE which API to use

**Process:**
1. Identifies domain (agriculture? finance? climate?)
2. Research available public APIs
3. Compares options (coverage, cost, quality)
4. **DECIDES** with justification
5. Documents decision

**Autonomy:** Claude decides without asking the user!

**Example of internal commands:**
```bash
# Claude executes internally:
WebSearch: "US agriculture API free historical data"
WebFetch: https://quickstats.nass.usda.gov/api
# Compares: NASS vs ERS vs FAO
# → DECISION: NASS (best option)
```

---

### PHASE 2: DESIGN (Analysis Definition)

**Objective:** DEFINE which analyses to implement

**Process:**
1. Brainstorm typical questions (10-15)
2. Group by type (comparisons, rankings, trends)
3. **DEFINES** 4-6 priority analyses
4. Specifies methodologies (mathematical formulas)

**Autonomy:** Claude prioritizes by value and frequency of use!

---

### PHASE 3: ARCHITECTURE (Structuring)

**Objective:** STRUCTURE the project optimally

**Process:**
1. Defines folder structure
2. Specifies scripts and responsibilities
3. Plans cache strategy
4. Defines validations

**Autonomy:** Claude chooses optimal architecture based on complexity!

---

### PHASE 4: DETECTION (Automatic Activation)

**Objective:** DETERMINE keywords for detection

**Process:**
1. Lists domain entities
2. Lists typical actions
3. Determines keywords
4. Creates optimized description (150-250 words)

**Result:** Skill activates automatically when user asks relevant question!

---

### PHASE 5: IMPLEMENTATION (Complete Code)

**Objective:** IMPLEMENT everything with REAL code

**Process:**
```bash
1. mkdir -p agent-name/{scripts/utils,references,assets,.claude-plugin}
2. Write: .claude-plugin/marketplace.json  ← REQUIRED!
3. Write: SKILL.md (5000+ words)
4. Write: scripts/*.py (functional code)
5. Write: utils/*.py (cache, validators, etc)
6. Write: references/*.md (useful content)
7. Write: assets/*.json (real configs)
8. Write: README.md + DECISIONS.md
```

**Quality Standards:**
- ✅ Complete code (no `TODO` or `pass`)
- ✅ Detailed docstrings
- ✅ Robust error handling
- ✅ Type hints
- ✅ Comprehensive validations

**Result:** Production-ready agent!

---

## 📝 Step-by-Step Commands

### 1. Create an Agent

**In Claude Code:**
```
👤 "Create an agent for [objective]"

OR

👤 "Automate this workflow: [description]"
```

### 2. Wait for Creation

Claude executes the 5 phases autonomously (~60-90 min)

### 3. Install Created Agent

**In terminal:**
```bash
# Go to agent directory
cd ./created-agent-name/

# Install Python dependencies
pip install -r requirements.txt

# If API key needed (follow instructions in README)
export API_KEY_VAR="your_key_here"
```

**In Claude Code:**
```bash
# Install skill
/plugin marketplace add ./created-agent-name

# Verify installation
/plugin list
```

### 4. Use the Agent

**In Claude Code:**
```
👤 Ask questions related to the domain
🤖 Skill activates automatically and responds
```

---

## 🎯 ROI (Return on Investment)

| Metric | Manual | With Agent-Creator | Savings |
|---------|--------|-------------------|----------|
| **Time** | 20-30 hours | 1.5 hours | **15-20x** |
| **Required knowledge** | APIs, Python, Architecture | None | **100%** |
| **Code written** | By you | By Claude | **100%** |
| **Quality** | Variable | Production-ready | High |

**But the best part:** You do nothing, just describe the workflow! 🎉

---

## 📚 Complete Documentation

This repository includes detailed guides in Portuguese:

1. **[como-compartilhar-skills.md](./como-compartilhar-skills.md)**
   - How to publish your skills
   - GitHub, ZIP, Claude.ai
   - Best practices

2. **[guia-completo-claude-skills.md](./guia-completo-claude-skills.md)**
   - Complete guide about Claude Skills
   - Technical specifications
   - Examples

3. **[como_instalar_agente_creator.md](./como_instalar_agente_creator.md)**
   - Detailed installation instructions
   - Troubleshooting

4. **[meta-prompt-autonomo-criacao-agentes.md](./meta-prompt-autonomo-criacao-agentes.md)**
   - Meta-prompt for agent creation
   - Universal annotated template
   - Quality checklist

5. **[scripts-vs-skills-guia-didatico.md](./scripts-vs-skills-guia-didatico.md)**
   - Didactic comparison Scripts vs Skills
   - When to use each approach

6. **[agent-creator/README.md](./agent-creator/README.md)**
   - Meta-skill documentation
   - Technical details

---

## 💡 Use Cases

### Agriculture
```
"Create agent for Brazilian crop analysis via CONAB"
→ Agent with TXT parsing, YoY analyses, regional rankings
```

### Finance
```
"Automate daily stock analysis: prices, RSI, MACD"
→ Agent with technical indicators, alerts, comparisons
```

### Climate
```
"Climate analysis of Sorriso-MT: temperature, rain, trends"
→ Agent with data since 1940, 6 types of analyses
```

### Economy
```
"Agent for World Bank economic indicators"
→ Agent with GDP, inflation, country comparisons
```

**Any domain with API or structured data!**

---

## 🛠️ Useful Commands

### Check Installed Skills
```bash
# In Claude Code
/plugin list
```

### Install Agent-Creator
```bash
# In Claude Code
/plugin marketplace add FrancyJGLisboa/agent-creator-skill
```

### Create an Agent
```bash
# In Claude Code (natural language)
"Create an agent for [objective]"
"Automate workflow of [description]"
```

### Install Created Agent
```bash
# Terminal
cd ./created-agent/
pip install -r requirements.txt

# Claude Code
/plugin marketplace add ./created-agent
```

### Use Agent
```bash
# In Claude Code (natural language)
Ask questions related to the agent's domain
```

---

## ⚙️ Technical Requirements

### To Use Agent-Creator
- Claude Code CLI installed
- Internet connection (for API research)

### For Created Agents
- Python 3.8+
- pip (to install dependencies)
- Specific dependencies (listed in requirements.txt of each agent)
- API key (if chosen API requires - instructions in agent's README)

---

## 🎓 Understanding the Output

### Main Files Created

**`.claude-plugin/marketplace.json`**
- Configuration for Claude Code installation
- **CRITICAL:** Without it, skill cannot be installed

**`SKILL.md`**
- Complete skill orchestration
- Detailed workflows
- Analysis documentation
- ~5000-7000 words

**`scripts/`**
- Functional Python code
- Separated by responsibility (fetch, parse, analyze)
- Reusable utils (cache, validators)
- ~1500-2000 lines total

**`references/`**
- Technical guides (API docs, methodologies)
- Troubleshooting
- Domain knowledge
- ~5000 words

**`README.md`**
- Installation instructions
- Usage examples
- Troubleshooting

**`DECISIONS.md`**
- Justifications for all decisions
- Which API chosen and why
- Which analyses and why
- Trade-offs considered

---

## ⭐ Features

- ✅ **Total Autonomy:** Claude decides everything
- ✅ **Production-Ready:** Functional code, no TODOs
- ✅ **Complete Documentation:** 10,000+ words
- ✅ **Smart Cache:** TTL based on data type
- ✅ **Robust Validations:** Guaranteed data quality
- ✅ **Error Handling:** Retry, fallbacks, clear messages
- ✅ **Marketplace.json:** Guaranteed Claude Code installation

---

## 🚧 Limitations

**DO NOT use for:**
- ❌ Editing existing skills (edit directly)
- ❌ Debugging skills (debug directly)
- ❌ Asking questions about skills (ask directly)

**USE ONLY for:**
- ✅ Creating new agents from scratch
- ✅ Automating repetitive workflows

---

## 🤝 Contributing

Contributions are welcome!

1. Fork this repository
2. Create a branch (`git checkout -b feature/improvement`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

Apache 2.0 (same license as Anthropic's official skills)

Free to use, modify, and distribute.

---

## 🙏 Credits

**Inspired by:**
- [Anthropic Agent Skills Spec](https://github.com/anthropics/skills)
- [skill-creator skill](https://github.com/anthropics/skills/tree/main/skill-creator)

**Differentiator:** Total autonomy - Claude decides everything, not just executes instructions.

---

## 📊 Repository Statistics

**Agent-Creator Meta-Skill:**
- 8 main files
- ~5,000 words in SKILL.md
- 6 detailed references
- 5-phase autonomous protocol

**Documentation:**
- 5 complete guides in Portuguese
- ~150 KB of documentation
- Complete coverage of Claude Skills ecosystem

---

## 🌟 Examples of Agents Created with Agent-Creator

**1. USDA Agriculture Agent**
- API: USDA NASS
- Analyses: YoY, Ranking, Trends
- Output: 1,410 lines of code

**2. Climate Analysis Sorriso-MT** (created today!)
- API: Open-Meteo
- Analyses: 6 types (series, trends, anomalies, etc.)
- Output: 2,070 lines of code

**All created autonomously by the meta-skill!**

---

## 📞 Support

**Issues:** https://github.com/FrancyJGLisboa/agent-creator-skill/issues
**Discussions:** https://github.com/FrancyJGLisboa/agent-creator-skill/discussions

---

## 🚀 Quick Start

```bash
# 1. Install agent-creator
/plugin marketplace add FrancyJGLisboa/agent-creator-skill

# 2. Create an agent (in Claude Code)
"Automate workflow for analyzing [your domain]"

# 3. Wait for creation (~60-90 min)

# 4. Install created agent
/plugin marketplace add ./created-agent

# 5. Use it!
"[Ask domain questions]"
```

---

**Start automating today! Transform repetitive workflows into powerful agents! 🚀**

---

**Version:** 1.0.0
**Updated:** October 2025
**Author:** Created with Claude Code
**Repository:** https://github.com/FrancyJGLisboa/agent-creator-skill

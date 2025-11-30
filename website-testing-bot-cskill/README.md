# Website Testing Bot

**Ultimate Commercial Readiness Assessment Tool**

A comprehensive website testing skill that performs exhaustive analysis of every site element, providing detailed reports with explicit fix instructions suitable for agent handoff.

## Overview

The Website Testing Bot answers three critical questions before commercial launch:

1. **Commercial Readiness Grade (A+ to F)**: Can this website handle commercial-scale usage?
2. **Uniqueness Score (1-100)**: Is this website unique or a cookie-cutter template?
3. **Readiness Status**: Is this website ready to launch? (Under Construction / Needs Polishing / Ready)

## Features

### Element Testing
- Buttons (functionality, accessibility, states)
- Links (validation, broken link detection, security)
- Images (alt text, optimization, loading)
- Forms (labels, validation, security)
- Menus (structure, accessibility, navigation)

### Performance Testing
- Core Web Vitals (LCP, FID, CLS)
- Load time measurement
- Concurrent user capacity estimation
- Resource optimization analysis

### Security Testing
- SSL/TLS validation
- Security header analysis
- Cookie security
- Vulnerability scanning

### Accessibility Testing
- WCAG 2.1 AA compliance
- Screen reader compatibility
- Keyboard navigation
- Color contrast

### Uniqueness Analysis
- Template detection
- Framework identification
- Originality scoring
- Customization assessment

### Agent Handoff Reports
- Zero-assumption fix instructions
- Step-by-step remediation guides
- Verification steps
- Priority-ordered issue lists

## Usage

### Basic Usage
```
Test my website at https://example.com for commercial readiness
```

### Advanced Usage
```
Perform a comprehensive audit of https://example.com including:
- Full element testing
- Performance benchmarking with load capacity estimation
- Security vulnerability scan
- WCAG AA accessibility compliance check
- Uniqueness score

Generate a detailed agent handoff report with explicit fix instructions.
```

## Grading System

### Commercial Readiness (A+ to F)
| Grade | Users | Response | Description |
|-------|-------|----------|-------------|
| A+ | 100k+ | <100ms | Enterprise-ready |
| A | 50k-100k | <200ms | Production-ready |
| B+ | 25k-50k | <500ms | Near-ready |
| B | 10k-25k | <1s | Viable |
| C+ | 5k-10k | <2s | Developing |
| C | 1k-5k | <3s | Early stage |
| D | <1k | >3s | Not ready |
| F | N/A | N/A | Critical issues |

### Uniqueness Score (1-100)
| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Highly Original | Custom design, unique functionality |
| 75-89 | Distinctive | Customized template with modifications |
| 50-74 | Moderate | Recognizable template base |
| 25-49 | Generic | Minimal customization |
| 1-24 | Template Clone | Nearly unmodified template |

### Readiness Status
- **READY**: All critical tests pass, approved for launch
- **NEEDS POLISHING**: Functional but has issues to address
- **UNDER CONSTRUCTION**: Significant issues preventing use

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m scripts.main https://example.com
```

## Output

The bot generates:
1. **JSON Report**: Complete test results with all data
2. **Agent Handoff Document**: Fix instructions for another agent
3. **Summary**: Quick overview of grades and status

## Architecture

```
website-testing-bot-cskill/
├── scripts/
│   ├── main.py              # Main orchestrator
│   ├── crawlers/            # Site discovery
│   ├── testers/             # Element testing
│   ├── analyzers/           # Grading and analysis
│   ├── reporters/           # Report generation
│   └── utils/               # Utilities
├── SKILL.md                 # Technical documentation
├── requirements.txt         # Dependencies
└── .claude-plugin/
    └── marketplace.json     # Activation config
```

## License

Part of the Agent Skill Creator ecosystem.

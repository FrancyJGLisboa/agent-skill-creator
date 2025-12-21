# Home Plant Trainer

Adaptive Residential Plant Design Advisor for Home Landscapes

## Overview

Home Plant Trainer is a comprehensive plant-only design system for residential landscapes. It provides zone-aware, condition-driven plant recommendations that automatically adapt based on:

- USDA Hardiness Zone (3-10)
- Sun Exposure (full, part, shade)
- Water Requirements (dry, average, wet)
- Size Constraints (height and width limits)
- Design Style (Traditional, Farmhouse, Craftsman, Modern, Cottage, Naturalistic)

**Important:** This skill focuses exclusively on plant design - no hardscape recommendations (patios, walls, pavers, walkways, etc.).

## Key Features

### Plant Role Matrix

Every landscape design uses consistent plant roles:

| Role | Description | Typical Height |
|------|-------------|----------------|
| **Structural** | Backbone plants for year-round structure | 3-8 ft |
| **Accent** | Focal points and seasonal color | 1-6 ft |
| **Screening** | Privacy and visual buffering | 6-25 ft |
| **Foundation** | Softens home architecture | 2-5 ft |
| **Edge/Border** | Clean transitions and bed edges | 0.5-1.5 ft |
| **Groundcover** | Soil coverage and weed suppression | 2-12 in |
| **Canopy** | Overhead trees for shade | 20-60 ft |
| **Understory** | Mid-layer small trees | 10-25 ft |

### Automatic Zone Adaptation

The core design principle: **Design intent stays constant - plants adapt.**

When you specify your zone and conditions, the system:
1. Filters plants that won't survive
2. Scores remaining options by fit
3. Recommends the best matches for each role

### Style-Based Design

Six design styles with complete guidance:

- **Traditional/Colonial**: Formal, balanced, symmetrical
- **Farmhouse**: Informal, naturalistic, textured
- **Craftsman**: Layered, natural, horizontal emphasis
- **Modern**: Minimal, architectural, repetitive
- **Cottage**: Abundant, romantic, flowing
- **Naturalistic**: Native, ecological, meadow-like

## Quick Start

### Create a Complete Design

```python
from scripts.main import HomePlantTrainer

trainer = HomePlantTrainer()

# Create a front yard design
design = trainer.create_design(
    location="front_yard",
    style="craftsman",
    zone="7a",
    sun="full",
    water="average",
    maintenance="low"
)

print(design["client_explanation"])
```

### Get Plants for a Specific Role

```python
# Find structural plants for zone 6
plants = trainer.get_plants_for_role(
    role="structural",
    zone="6b",
    sun="part",
    water="average"
)

for plant in plants:
    print(f"{plant['plant_name']}: {plant['reasoning']}")
```

### Find Plant Swap Alternatives

```python
# Find alternatives for Japanese Maple in zone 4
alternatives = trainer.swap_plant(
    plant_name="Japanese Maple",
    zone="4a",
    sun="part",
    water="average"
)

for alt in alternatives["alternatives"]:
    print(f"{alt['plant_name']}: {alt['why_it_works']}")
```

### Get Style Guide

```python
# Get craftsman style guidance
guide = trainer.get_style_guide("craftsman")

print(guide["description"])
print(guide["principles"])
```

## Command Line Usage

```bash
# Create a design
python scripts/main.py design front_yard craftsman 7a full average

# Get plants for a role
python scripts/main.py role structural 6b full average

# Find swap alternatives
python scripts/main.py swap "Japanese Maple" 4a part average

# Get style guide
python scripts/main.py style farmhouse

# Get role specification
python scripts/main.py rolespec screening
```

## Example Queries

The skill responds to queries like:

**Plant Selection by Zone:**
- "What structural plants work in zone 6 full sun?"
- "Recommend foundation plants for zone 8"

**Condition-Based Queries:**
- "Drought tolerant shrubs for full sun zone 9"
- "Shade plants that handle wet soil in zone 5"

**Style-Based Design:**
- "Craftsman landscape plants for zone 7"
- "Modern minimalist planting palette"

**Plant Swap Requests:**
- "Swap boxwood for zone 4"
- "Alternative to Japanese maple for full sun zone 8"
- "What can I use instead of knockout roses?"

**Location-Based Design:**
- "Front yard curb appeal plants zone 7"
- "Backyard privacy screen plants full sun"
- "Side yard transition planting shade"

**Natural Language:**
- "Help me choose plants for my front yard in zone 6"
- "What plants should I use to screen my neighbor?"
- "Create a planting plan for curb appeal"

## Design Philosophy

This skill integrates principles from respected landscape design sources:

### Better Homes & Gardens
- Home-integrated landscape principles
- Front yard curb appeal strategies
- Backyard outdoor living design

### Sunset Magazine
- Regional and climate-aware design
- Plant selection by growing conditions

### Architectural Digest
- High-end design perspectives
- Integration of garden and architecture

### Professional Sources
- **Yardzen**: Style classification system
- **Houzz**: Real-world project examples
- **Landscaping Network**: Professional design workflows

### Design Foundations
- **Frederick Law Olmsted**: Human-centric, naturalistic design
- **Oehme, van Sweden**: New American Garden principles
- **The Cultural Landscape Foundation**: Professional practice context

## Core Rules

### 1. Design Intent is Constant
The design framework (roles, layering, style) remains the same regardless of zone. Only plant species change.

### 2. Size is Non-Negotiable
If a space has height or width limits, plants exceeding those limits are never recommended.

### 3. Role Integrity
Plants aren't swapped across roles (e.g., a screening plant for an accent). Each role has specific requirements.

### 4. Condition Matching
Zone, sun, and water requirements must match. There are no exceptions for "maybe it'll work."

### 5. Style Consistency
All recommendations reinforce the chosen design style vocabulary.

## Plant Database

The skill includes 60+ carefully selected residential landscape plants covering:

- **Zones**: 3-11
- **Sun**: Full, Part, Shade
- **Water**: Dry, Average, Wet
- **Roles**: All 8 design roles
- **Styles**: All 6 design styles

Plant data includes:
- Zone tolerance ranges
- Sun/water/soil requirements
- Mature size specifications
- Form and growth characteristics
- Seasonal interest by season
- Maintenance requirements
- Deer/salt tolerance
- Native regions
- Wildlife value

## Proposal Explanation Engine

Every design includes client-ready explanations:

```
## Design Intent

This planting plan is designed to create a cohesive, home-integrated
landscape with year-round structure and seasonal interest.

**Style Approach: Craftsman**
Layered, natural material harmony with strong horizontal lines...

## Site Conditions

Plant selections are matched to your property's specific conditions:
- USDA Hardiness Zone: 7a
- Sun Exposure: Full
- Moisture Profile: Average
- Target Maintenance Level: Low

## Plant Selection Rationale

### Structural Layer
**Yew** (Taxus x media)
- Form: Upright
- Mature Size: 8H x 6W ft
- Selection Factors: Matches structural role | Year-round structure...
```

## File Structure

```
home-plant-trainer-cskill/
├── .claude-plugin/
│   └── marketplace.json      # Skill configuration and activation patterns
├── scripts/
│   ├── main.py               # Main interface and CLI
│   └── utils/
│       ├── __init__.py
│       ├── plant_database.py # Comprehensive plant data
│       └── design_advisor.py # Style packages and explanation engine
├── references/               # Source documentation
├── SKILL.md                  # Technical specification
└── README.md                 # This file
```

## Contributing

To add new plants:
1. Edit `scripts/utils/plant_database.py`
2. Add a new `Plant` object with all required fields
3. Ensure zone, sun, water, and size data is accurate
4. Assign appropriate roles and style tags

To add new styles:
1. Edit `scripts/utils/design_advisor.py`
2. Add a new `StylePackage` to `STYLE_PACKAGES`
3. Define all style attributes (principles, forms, colors, etc.)

## License

Internal use only. Design principles attributed to source publications.

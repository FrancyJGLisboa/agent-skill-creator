# Home Plant Trainer - Technical Specification

## Overview

Home Plant Trainer is an adaptive residential plant design advisor for home landscapes. It provides zone-aware, condition-driven plant selection with automatic species swapping based on USDA hardiness zones, sun exposure, water requirements, and size constraints.

**Key Principle**: Design intent stays constant. Plant species change based on site conditions.

**Focus**: Plant-only designs - no hardscape recommendations.

## Architecture

### Directory Structure

```
home-plant-trainer-cskill/
├── .claude-plugin/
│   └── marketplace.json       # Plugin configuration with activation
├── SKILL.md                   # This technical specification
├── README.md                  # User guide
├── requirements.txt           # Dependencies
├── scripts/
│   ├── main.py               # Main orchestrator (HomePlantTrainer class)
│   ├── plant_database.py     # Plant data with 50+ species
│   ├── design_advisor.py     # Style packages and AI prompts
│   └── utils/
│       ├── __init__.py
│       └── helpers.py        # Validation and formatting utilities
└── references/               # Additional documentation
```

### Core Components

#### 1. HomePlantTrainer (main.py)

Primary orchestrator class that coordinates all design functions.

**Key Methods:**
- `design_planting()` - Create complete planting designs
- `recommend_plants()` - Get role-specific recommendations
- `swap_plant()` - Find climate-adapted alternatives
- `get_style_guide()` - Retrieve style documentation
- `get_space_guide()` - Get yard space guidance
- `get_role_guide()` - Understand plant roles

#### 2. PlantRoleMatrix (main.py)

Defines the 8 plant roles used in residential design:

| Role | Description | Height Range | Key Attributes |
|------|-------------|--------------|----------------|
| STRUCTURAL | Year-round backbone | 3-8 ft | Dense, prunable |
| ACCENT | Focal points, seasonal punch | 1-6 ft | Bloom/texture priority |
| SCREENING | Privacy, buffering | 6-25 ft | Dense, reliable |
| FOUNDATION_SOFTENER | Reduce harsh lines | 2-5 ft | Window-friendly |
| EDGE_BORDER | Bed lines, transitions | 0.5-1.5 ft | Tidy habit |
| GROUNDCOVER | Soil cover, unification | 2-12 in | Spreading, erosion control |
| CANOPY | Overhead structure | 20-60 ft | Setback-appropriate |
| UNDERSTORY | Mid-layer depth | 10-25 ft | Shade tolerant |

#### 3. StylePackages (main.py)

Six residential design styles:

- **Traditional/Colonial** - Symmetry, formal hedges, classic palette
- **Farmhouse** - Informal grouping, native species, naturalized
- **Craftsman** - Layered evergreens, horizontal lines, earth tones
- **Modern** - Minimal palette, repetition, architectural forms
- **Cottage** - Dense borders, abundant bloom, romantic
- **Naturalistic** - Native focus, wildlife support, low input

#### 4. AutoSwapEngine (main.py)

Handles plant substitution logic:

**Hard Filters (Must Pass):**
- Zone compatibility
- Sun exposure match
- Water profile match
- Size constraints

**Soft Scoring:**
- Maintenance level match
- Drought tolerance (for dry sites)
- Deer resistance (when flagged)
- Evergreen preference (for structural roles)
- Size efficiency

#### 5. Plant Database (plant_database.py)

50+ residential plants with full metadata:

```python
@dataclass
class PlantRecommendation:
    botanical_name: str
    common_name: str
    role: PlantRole
    layer: PlantLayer
    form: PlantForm
    mature_height_ft: float
    mature_width_ft: float
    zone_min: int
    zone_max: int
    sun_options: List[str]
    water_options: List[str]
    evergreen: bool
    seasonal_interest: List[str]
    maintenance_level: str
    deer_resistant: bool
    drought_tolerant: bool
    native_regions: List[str]
    design_notes: str
```

#### 6. Design Advisor (design_advisor.py)

Style-specific guidance and AI prompt generation:

- `ResidentialDesignAdvisor` - Design packages and briefs
- `AIPromptGenerator` - Prompts for AI-assisted design
- `PlantPaletteBuilder` - Curated palettes (pollinator, low-water, shade, four-season)

## Data Flow

```
User Input
    ↓
Validation & Normalization (utils/helpers.py)
    ↓
Site Conditions Object
    ↓
Style & Space Selection
    ↓
Plant Database Query
    ↓
AutoSwapEngine Filtering & Scoring
    ↓
ProposalExplanationEngine
    ↓
Design Output with Explanations
```

## Activation System

### Layer 1: Keywords (75 keywords)

Organized into 6 categories:
1. Core plant design (15)
2. Zone and condition (15)
3. Plant role and layer (15)
4. Space and location (12)
5. Style and design (10)
6. Natural language (8)

### Layer 2: Patterns (14 regex patterns)

Covering:
- Plant selection by zone
- Plant selection by condition
- Plant role queries
- Space-based design
- Style-based design
- Plant swap/substitution
- Layered planting
- Size constraints
- Home integration
- Maintenance levels
- Seasonal interest
- Natural language design help
- Wildlife/ecosystem
- Problem-solving

### Context Filters

**Required Context:**
- Domains: residential landscaping, home gardening, plant design
- Tasks: plant selection, design recommendation, zone adaptation

**Excluded Context:**
- Domains: commercial landscaping, hardscape design, construction
- Tasks: patio installation, irrigation systems

## API Reference

### design_planting()

Create a complete planting design.

```python
result = trainer.design_planting(
    zone=7,                    # USDA zone (3-10)
    sun="full",                # full, part, shade
    water="average",           # dry, average, wet
    space="front_yard",        # front_yard, backyard, side_yard
    style="craftsman",         # design style
    height_limit=20.0,         # max height in feet
    width_limit=10.0,          # max width in feet
    maintenance="medium",      # low, medium, high
    deer_pressure=False,       # deer concern
    zone_suffix=""             # a or b suffix
)
```

**Returns:**
```python
{
    "design": {
        "space": "front_yard",
        "style": "craftsman",
        "zone": "7",
        "conditions": {"sun": "full", "water": "average", "maintenance": "medium"}
    },
    "plants": [...],           # List of plant recommendations
    "plant_summary": {
        "total_count": 8,
        "by_role": {...},
        "by_layer": {...},
        "evergreen_count": 5,
        "deciduous_count": 3
    },
    "explanations": {
        "design_intent": "...",
        "site_constraints": "...",
        "maintenance": "...",
        "layers": "..."
    },
    "design_notes": "...",
    "timestamp": "..."
}
```

### recommend_plants()

Get plants for a specific role.

```python
plants = trainer.recommend_plants(
    role="structural",         # Plant role
    zone=6,                    # USDA zone
    sun="part",                # Sun exposure
    water="average",           # Water profile
    height_limit=8.0,          # Max height
    width_limit=6.0,           # Max width
    count=5                    # Number to return
)
```

### swap_plant()

Find alternatives for a plant.

```python
result = trainer.swap_plant(
    plant_name="boxwood",      # Plant to replace
    zone=4,                    # Target zone
    sun="full",                # Target sun
    water="average",           # Target water
    height_limit=6.0,          # Max height
    width_limit=6.0            # Max width
)
```

**Returns:**
```python
{
    "original": {...},         # Original plant details
    "compatible": False,       # Whether original works
    "issues": [...],           # Why it doesn't work
    "alternatives": [
        {
            "botanical_name": "...",
            "common_name": "...",
            "match_score": 0.85,
            "swap_reason": "...",
            "justification": "..."
        }
    ]
}
```

## Design Principles

### Training Rules

1. **Design intent stays constant** - Only species change, not design structure
2. **Form, scale, and role never change** - Maintain visual impact
3. **Layer hierarchy stays identical** - Same vertical structure
4. **Water tolerance overrides zone** - If drainage is poor
5. **Shade designs rely on foliage** - Not flowers
6. **Reject plants exceeding spatial envelope** - Size is non-negotiable

### Plant Selection Priority

1. Zone compatibility (hard requirement)
2. Sun/water match (hard requirement)
3. Size constraints (hard requirement)
4. Role match (critical for design)
5. Style alignment (important)
6. Maintenance fit (preference)
7. Special tolerances (deer, drought, salt)

### Swap Logic

When swapping plants:
1. Never swap across roles unless no options exist
2. Maintain same layer position
3. Match form as closely as possible
4. Preserve seasonal interest timing
5. Generate client-ready justification

## Source Attribution

Design principles derived from:
- Better Homes & Gardens
- Sunset Magazine
- Houzz
- Yardzen
- Landscaping Network
- Architectural Digest
- Frederick Law Olmsted principles
- The Cultural Landscape Foundation
- Oehme, van Sweden design philosophy

## Performance

- Plant database: 50+ species
- Query response: <100ms for recommendations
- Swap search: <200ms for 3 alternatives
- Full design: <500ms for complete plan

## Extensibility

### Adding Plants

Add to `plant_database.py`:

```python
PlantRecommendation(
    botanical_name="Genus species",
    common_name="Common Name",
    role=PlantRole.STRUCTURAL,
    layer=PlantLayer.SHRUB,
    form=PlantForm.ROUNDED,
    mature_height_ft=5.0,
    mature_width_ft=5.0,
    zone_min=5,
    zone_max=9,
    sun_options=["full", "part"],
    water_options=["average"],
    evergreen=True,
    seasonal_interest=["spring", "summer", "fall", "winter"],
    maintenance_level="low",
    deer_resistant=True,
    drought_tolerant=False,
    native_regions=["Eastern US"],
    design_notes="Design-relevant notes here."
)
```

### Adding Styles

Add to `StylePackages.STYLES` in `main.py`:

```python
DesignStyle.NEW_STYLE: {
    "name": "New Style Name",
    "principles": ["principle1", "principle2"],
    "plant_characteristics": {...},
    "spacing_style": "style_approach",
    "color_palette": [...]
}
```

## Test Queries

Core functionality:
- "What structural plants work in zone 6 full sun?"
- "Create a front yard planting plan for zone 8"
- "Recommend foundation plants for a craftsman home"

Condition-based:
- "Drought tolerant shrubs for full sun zone 9"
- "Shade plants that handle wet soil in zone 6"

Style-based:
- "Farmhouse style garden plants for zone 6"
- "Modern minimalist planting palette"

Plant swap:
- "Swap boxwood for zone 4"
- "Alternative to Japanese maple for full sun zone 8"

## Version History

- **1.0.0** (2025-12-21)
  - Initial release
  - 50+ plant database
  - 6 design styles
  - 8 plant roles
  - Full auto-swap engine
  - Proposal explanation engine

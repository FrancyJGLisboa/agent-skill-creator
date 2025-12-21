# Home Plant Trainer - Technical Specification

## Skill Overview

**Name:** home-plant-trainer-cskill
**Version:** 1.0.0
**Type:** Adaptive Residential Plant Design Advisor
**Focus:** Plant-only designs for home landscapes (no hardscape)

## Core Capabilities

### 1. Plant Role Matrix

Universal plant role system that works across all zones:

| Role | Layer | Height Range | Description |
|------|-------|--------------|-------------|
| Structural | Shrub | 3-8 ft | Backbone - holds design together year-round |
| Accent | Herbaceous | 1-6 ft | Focal points, seasonal punch, visual moments |
| Screening | Understory | 6-25 ft | Privacy, view control, visual buffering |
| Foundation | Shrub | 2-5 ft | Softens architectural lines at home base |
| Edge/Border | Groundcover | 0.5-1.5 ft | Clean bed lines, lawn transitions |
| Groundcover | Groundcover | 0.15-1 ft | Covers soil, suppresses weeds, unifies |
| Canopy | Canopy | 20-60 ft | Overhead structure, microclimate builder |
| Understory | Understory | 10-25 ft | Mid-layer for depth and seasonal interest |

### 2. Adaptive Selection Engine

Three-step selection process:

**Step A: Non-negotiable Filters (Hard Fails)**
- USDA zone must be within plant's range
- Sun exposure must match
- Water profile must match
- Size must not exceed limits

**Step B: Preference Scoring (Soft Ranking)**
- Role match: +10 points
- Evergreen bonus (structural roles): +3 points
- Maintenance match: +2 points
- Deer resistance (if needed): +2.5 points
- Drought tolerance (dry sites): +2 points
- Soil tolerance match: +1.5 points
- Style match: +2 points
- Form match: +1.5 points

**Step C: Design Integrity Lock**
- Never swap across roles unless no options exist
- Fallback order defined per role
- Role preservation maintains design intent

### 3. Style Packages

Six design styles with complete specifications:

| Style | Description | Key Forms | Spacing |
|-------|-------------|-----------|---------|
| Traditional | Formal, balanced, symmetric | Rounded, columnar | Regular, geometric |
| Farmhouse | Informal, naturalistic | Mounding, fountain | Irregular, natural |
| Craftsman | Layered, horizontal harmony | Layered, upright | Grouped, horizontal |
| Modern | Minimal, architectural | Columnar, linear | Precise, generous gaps |
| Cottage | Abundant, romantic | Mounding, billowing | Close, intermingled |
| Naturalistic | Native, ecological | Natural, fountain | Drifts, community-based |

### 4. Location-Based Design Models

**Front Yard / Curb Appeal**
- Primary function: First impression, entry framing
- Essential roles: Structural, Foundation, Accent, Edge
- Priority: Architectural harmony, clear sight lines

**Backyard / Outdoor Living**
- Primary function: Privacy, outdoor rooms, shade
- Essential roles: Canopy, Screening, Structural, Accent, Groundcover
- Priority: Privacy screening, shade provision

**Side Yard / Transition Zone**
- Primary function: Utility, screening, design continuity
- Essential roles: Screening, Structural, Groundcover
- Priority: Low maintenance, visual screening

## Data Schema

### Plant Record Structure

```python
@dataclass
class Plant:
    # Identification
    common_name: str
    botanical_name: str

    # Climate Tolerance
    zone_min: int                    # USDA zone minimum
    zone_max: int                    # USDA zone maximum

    # Requirements
    sun_tolerance: List[str]         # ["full", "part", "shade"]
    water_tolerance: List[str]       # ["dry", "average", "wet"]
    soil_tolerance: List[str]        # ["clay", "loam", "sand"]

    # Size
    mature_height_ft: float
    mature_width_ft: float

    # Design Attributes
    form: str                        # rounded, upright, spreading, etc.
    roles: List[str]                 # structural, accent, etc.
    style_tags: List[str]            # traditional, modern, etc.

    # Maintenance
    maintenance_level: str           # low, medium, high
    deer_resistant: bool
    salt_tolerant: bool

    # Features
    evergreen: bool
    native_regions: List[str]
    wildlife_value: bool
    seasonal_interest: Dict[str, str]
```

### Site Conditions Structure

```python
@dataclass
class SiteConditions:
    usda_zone: str                   # e.g., "6b", "7a"
    sun_exposure: SunExposure        # full, part, shade
    water_profile: WaterNeeds        # dry, average, wet
    soil_type: SoilType              # clay, loam, sand
    height_limit_ft: Optional[float]
    width_limit_ft: Optional[float]
    maintenance_level: MaintenanceLevel
    wind_exposed: bool
    salt_exposure: bool
    deer_pressure: bool
```

### Design Request Structure

```python
@dataclass
class DesignRequest:
    location: YardLocation           # front_yard, backyard, side_yard
    style: DesignStyle               # traditional, farmhouse, etc.
    site_conditions: SiteConditions
    roles_needed: List[PlantRole]
    year_round_structure: bool
    seasonal_priority: Optional[str]
    wildlife_friendly: bool
    native_preference: bool
```

## API Reference

### HomePlantTrainer Class

**create_design()**
```python
def create_design(
    location: str,          # "front_yard", "backyard", "side_yard"
    style: str,             # "traditional", "farmhouse", etc.
    zone: str,              # "6b", "7a", etc.
    sun: str,               # "full", "part", "shade"
    water: str,             # "dry", "average", "wet"
    roles: List[str] = None,
    height_limit: float = None,
    width_limit: float = None,
    maintenance: str = "medium",
    year_round: bool = True,
    wildlife: bool = False,
    native: bool = False
) -> Dict[str, Any]
```

**get_plants_for_role()**
```python
def get_plants_for_role(
    role: str,              # "structural", "accent", etc.
    zone: str,
    sun: str,
    water: str,
    style: str = None,
    height_limit: float = None,
    width_limit: float = None,
    count: int = 5
) -> List[Dict[str, Any]]
```

**swap_plant()**
```python
def swap_plant(
    plant_name: str,
    zone: str,
    sun: str,
    water: str,
    height_limit: float = None,
    width_limit: float = None,
    count: int = 3
) -> Dict[str, Any]
```

**get_style_guide()**
```python
def get_style_guide(style: str) -> Dict[str, Any]
```

**get_role_specification()**
```python
def get_role_specification(role: str) -> Dict[str, Any]
```

## Design Philosophy Sources

This skill integrates design principles from highly respected sources:

### Editorial/Home-Lifestyle Authority
- **Better Homes & Gardens**: Home-integrated landscape principles, curb appeal, outdoor living
- **Sunset Magazine**: Regional and climate-aware design strategies
- **Architectural Digest**: High-end design perspectives, integration principles

### Real-World Project Repositories
- **Houzz**: Practical project examples across architectural styles
- **Landscaping Network**: Professional design workflows and solutions

### Professional Style Systems
- **Yardzen**: Style classification and design vocabulary

### Design Philosophy & Foundations
- **Frederick Law Olmsted**: Human-centric, nature-integrated design
- **The Cultural Landscape Foundation**: Historical context and professional practice
- **Oehme, van Sweden**: New American Garden / sustainable design principles

## Core Design Rules

### Rule 1: Design Intent is Constant
Form, scale, and role never change - only species adapt to conditions.

### Rule 2: Non-Negotiable Filters
Zone, sun, water, and size constraints cannot be overridden.

### Rule 3: Role Integrity
Never swap across roles unless no options exist within the role.

### Rule 4: Style Consistency
All selections should reinforce the chosen design style vocabulary.

### Rule 5: Size Sovereignty
Mature plant size must fit within specified constraints - no exceptions.

## Activation Patterns

The skill activates on queries matching:

1. Plant selection by zone: "recommend plants for zone 7"
2. Plant selection by condition: "plants for full sun dry soil"
3. Plant role queries: "structural plants for front yard"
4. Space-based design: "backyard privacy planting"
5. Style-based design: "craftsman landscape plants"
6. Plant swap requests: "alternative to boxwood in zone 5"
7. Natural language: "help me choose plants for my front yard"

## Output Formats

### Design Output
```json
{
  "design_intent": "Description of design approach",
  "site_constraints": { ... },
  "style": "craftsman",
  "location": "front_yard",
  "plant_selections": {
    "structural": [...],
    "accent": [...],
    "foundation": [...],
    "groundcover": [...]
  },
  "seasonal_timeline": {
    "spring": [...],
    "summer": [...],
    "fall": [...],
    "winter": [...]
  },
  "maintenance_summary": "...",
  "client_explanation": "..."
}
```

### Plant Recommendation Output
```json
{
  "plant_name": "Japanese Maple",
  "botanical_name": "Acer palmatum",
  "form": "layered",
  "size": "15H x 15W ft",
  "score": 18.5,
  "reasoning": "Matches accent role | Evergreen for year-round | Matches craftsman style",
  "evergreen": false,
  "seasonal_interest": { ... }
}
```

### Swap Recommendation Output
```json
{
  "original_plant": "Boxwood",
  "original_info": { ... },
  "swap_reason": "Finding alternatives for Zone 4, full sun, dry water",
  "alternatives": [
    {
      "plant_name": "Inkberry Holly",
      "botanical_name": "Ilex glabra",
      "match_score": 17.5,
      "why_it_works": "Matches structural role | Native species | Cold hardy"
    }
  ]
}
```

## Version History

- **1.0.0** (2025-12-21): Initial release
  - Plant Role Matrix with 8 roles
  - 60+ plant database entries
  - 6 design style packages
  - 3 location-based design models
  - Adaptive selection engine
  - Client explanation engine

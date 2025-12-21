#!/usr/bin/env python3
"""
Plant Database for Home Plant Trainer

Comprehensive database of residential landscape plants with:
- USDA zone compatibility
- Sun/shade tolerance
- Water requirements
- Size specifications
- Role assignments
- Style tags
- Maintenance levels
- Seasonal interest

Based on design principles from Better Homes & Gardens, Sunset Magazine,
Architectural Digest, Houzz, and professional landscape resources.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Plant:
    """Complete plant specification for residential landscaping."""

    # Identification
    common_name: str
    botanical_name: str

    # Climate Tolerance
    zone_min: int                          # Minimum USDA zone
    zone_max: int                          # Maximum USDA zone

    # Light Requirements
    sun_tolerance: List[str]               # ["full", "part", "shade"]

    # Water Requirements
    water_tolerance: List[str]             # ["dry", "average", "wet"]

    # Soil Tolerance
    soil_tolerance: List[str] = field(default_factory=lambda: ["loam"])

    # Size at Maturity
    mature_height_ft: float = 0.0
    mature_width_ft: float = 0.0

    # Growth Characteristics
    form: str = "rounded"                  # rounded, upright, spreading, columnar, etc.
    growth_rate: str = "medium"            # slow, medium, fast
    evergreen: bool = False

    # Design Attributes
    roles: List[str] = field(default_factory=list)  # structural, accent, screening, etc.
    style_tags: List[str] = field(default_factory=list)  # traditional, modern, etc.

    # Maintenance
    maintenance_level: str = "medium"      # low, medium, high
    deer_resistant: bool = False
    salt_tolerant: bool = False

    # Special Features
    native_regions: List[str] = field(default_factory=list)
    wildlife_value: bool = False
    fragrant: bool = False

    # Seasonal Interest
    seasonal_interest: Dict[str, str] = field(default_factory=dict)
    # {"spring": "white flowers", "fall": "red foliage", etc.}

    # Additional Notes
    notes: str = ""


class PlantDatabase:
    """
    Database of plants for residential landscape design.

    Provides query methods for finding plants by:
    - Role
    - Zone compatibility
    - Condition requirements
    - Style preferences
    """

    def __init__(self):
        self.plants: Dict[str, Plant] = {}
        self._load_plants()

    def _load_plants(self):
        """Load all plant data."""
        plants = self._get_all_plants()
        for plant in plants:
            self.plants[plant.common_name.lower()] = plant

    def get_plant_by_name(self, name: str) -> Optional[Plant]:
        """Get a plant by common name."""
        return self.plants.get(name.lower())

    def get_plants_by_role(self, role) -> List[Plant]:
        """Get all plants that serve a specific role."""
        role_value = role.value if hasattr(role, 'value') else role
        return [p for p in self.plants.values() if role_value in p.roles]

    def get_plants_by_zone(self, zone: int) -> List[Plant]:
        """Get all plants compatible with a zone."""
        return [
            p for p in self.plants.values()
            if p.zone_min <= zone <= p.zone_max
        ]

    def get_plants_by_conditions(
        self,
        zone: int,
        sun: str,
        water: str
    ) -> List[Plant]:
        """Get plants matching specific conditions."""
        return [
            p for p in self.plants.values()
            if (p.zone_min <= zone <= p.zone_max and
                sun in p.sun_tolerance and
                water in p.water_tolerance)
        ]

    def get_all_plants(self) -> List[Plant]:
        """Get all plants in the database."""
        return list(self.plants.values())

    def _get_all_plants(self) -> List[Plant]:
        """Define all plants in the database."""
        return [
            # ================================================================
            # STRUCTURAL SHRUBS
            # ================================================================
            Plant(
                common_name="Boxwood",
                botanical_name="Buxus sempervirens",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=5.0,
                mature_width_ft=5.0,
                form="rounded",
                growth_rate="slow",
                evergreen=True,
                roles=["structural", "foundation", "edge"],
                style_tags=["traditional", "modern"],
                maintenance_level="medium",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Classic structural shrub, responds well to shearing"
            ),

            Plant(
                common_name="Inkberry Holly",
                botanical_name="Ilex glabra",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=6.0,
                mature_width_ft=6.0,
                form="rounded",
                growth_rate="slow",
                evergreen=True,
                roles=["structural", "foundation", "screening"],
                style_tags=["traditional", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "black berries",
                    "winter": "evergreen structure"
                },
                notes="Native alternative to boxwood, tolerates wet soils"
            ),

            Plant(
                common_name="Arborvitae",
                botanical_name="Thuja occidentalis",
                zone_min=3,
                zone_max=7,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=15.0,
                mature_width_ft=4.0,
                form="columnar",
                growth_rate="medium",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["traditional", "farmhouse"],
                maintenance_level="low",
                deer_resistant=False,
                native_regions=["northeastern US"],
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Excellent privacy screen, deer browse in winter"
            ),

            Plant(
                common_name="Emerald Green Arborvitae",
                botanical_name="Thuja occidentalis 'Smaragd'",
                zone_min=3,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=12.0,
                mature_width_ft=3.5,
                form="columnar",
                growth_rate="slow",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["traditional", "modern"],
                maintenance_level="low",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "bright green foliage",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Compact form, maintains color in winter"
            ),

            Plant(
                common_name="Yew",
                botanical_name="Taxus x media",
                zone_min=4,
                zone_max=7,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "sand"],
                mature_height_ft=8.0,
                mature_width_ft=6.0,
                form="upright",
                growth_rate="slow",
                evergreen=True,
                roles=["structural", "foundation", "screening"],
                style_tags=["traditional", "craftsman"],
                maintenance_level="medium",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "new growth flush",
                    "summer": "dark green foliage",
                    "fall": "red berries",
                    "winter": "evergreen structure"
                },
                notes="Classic foundation plant, tolerates heavy shade"
            ),

            Plant(
                common_name="Dwarf Yaupon Holly",
                botanical_name="Ilex vomitoria 'Nana'",
                zone_min=7,
                zone_max=10,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=3.0,
                mature_width_ft=4.0,
                form="mounding",
                growth_rate="slow",
                evergreen=True,
                roles=["structural", "foundation", "edge"],
                style_tags=["traditional", "modern", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Native, extremely adaptable, heat/drought tolerant"
            ),

            Plant(
                common_name="Loropetalum",
                botanical_name="Loropetalum chinense",
                zone_min=7,
                zone_max=10,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=6.0,
                mature_width_ft=6.0,
                form="rounded",
                growth_rate="medium",
                evergreen=True,
                roles=["structural", "accent"],
                style_tags=["modern", "craftsman"],
                maintenance_level="medium",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "pink/magenta flowers",
                    "summer": "burgundy foliage",
                    "fall": "burgundy foliage",
                    "winter": "evergreen structure"
                },
                notes="Provides year-round color with purple foliage"
            ),

            Plant(
                common_name="Japanese Holly",
                botanical_name="Ilex crenata",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=6.0,
                mature_width_ft=6.0,
                form="rounded",
                growth_rate="slow",
                evergreen=True,
                roles=["structural", "foundation"],
                style_tags=["traditional", "modern"],
                maintenance_level="medium",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "dark green foliage",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Boxwood alternative with similar form"
            ),

            Plant(
                common_name="Privet",
                botanical_name="Ligustrum japonicum",
                zone_min=7,
                zone_max=10,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=10.0,
                mature_width_ft=6.0,
                form="upright",
                growth_rate="fast",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["traditional"],
                maintenance_level="high",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "white fragrant flowers",
                    "summer": "evergreen structure",
                    "fall": "blue-black berries",
                    "winter": "evergreen structure"
                },
                fragrant=True,
                notes="Fast-growing screen, requires regular pruning"
            ),

            Plant(
                common_name="Pittosporum",
                botanical_name="Pittosporum tobira",
                zone_min=8,
                zone_max=11,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "sand"],
                mature_height_ft=10.0,
                mature_width_ft=10.0,
                form="rounded",
                growth_rate="medium",
                evergreen=True,
                roles=["structural", "screening"],
                style_tags=["modern", "traditional"],
                maintenance_level="low",
                deer_resistant=True,
                salt_tolerant=True,
                seasonal_interest={
                    "spring": "fragrant white flowers",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                fragrant=True,
                notes="Excellent for coastal areas, very drought tolerant"
            ),

            # ================================================================
            # ACCENT PLANTS
            # ================================================================
            Plant(
                common_name="Hydrangea",
                botanical_name="Hydrangea macrophylla",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam"],
                mature_height_ft=5.0,
                mature_width_ft=5.0,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["accent"],
                style_tags=["traditional", "cottage", "farmhouse"],
                maintenance_level="medium",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "emerging foliage",
                    "summer": "large blue/pink flowers",
                    "fall": "dried flower heads",
                    "winter": "architectural stems"
                },
                notes="Classic summer bloomer, flower color varies with soil pH"
            ),

            Plant(
                common_name="Oakleaf Hydrangea",
                botanical_name="Hydrangea quercifolia",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=6.0,
                mature_width_ft=8.0,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["accent", "structural"],
                style_tags=["naturalistic", "farmhouse", "craftsman"],
                maintenance_level="low",
                deer_resistant=False,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "emerging oak-shaped leaves",
                    "summer": "white cone-shaped flowers",
                    "fall": "burgundy/red foliage",
                    "winter": "exfoliating bark"
                },
                notes="Native, four-season interest, drought tolerant once established"
            ),

            Plant(
                common_name="Japanese Maple",
                botanical_name="Acer palmatum",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=15.0,
                mature_width_ft=15.0,
                form="layered",
                growth_rate="slow",
                evergreen=False,
                roles=["accent", "understory"],
                style_tags=["craftsman", "modern", "traditional"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "colorful emerging leaves",
                    "summer": "delicate foliage",
                    "fall": "brilliant red/orange color",
                    "winter": "graceful branching structure"
                },
                notes="Iconic specimen tree, protect from afternoon sun in hot zones"
            ),

            Plant(
                common_name="Knockout Rose",
                botanical_name="Rosa 'Radrazz'",
                zone_min=5,
                zone_max=10,
                sun_tolerance=["full"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=4.0,
                mature_width_ft=4.0,
                form="rounded",
                growth_rate="fast",
                evergreen=False,
                roles=["accent"],
                style_tags=["traditional", "cottage", "farmhouse"],
                maintenance_level="low",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "first flush of blooms",
                    "summer": "continuous red flowers",
                    "fall": "continued blooming",
                    "winter": "none"
                },
                notes="Disease-resistant, continuous bloomer spring through frost"
            ),

            Plant(
                common_name="Lavender",
                botanical_name="Lavandula angustifolia",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["dry"],
                soil_tolerance=["loam", "sand"],
                mature_height_ft=2.0,
                mature_width_ft=2.0,
                form="mounding",
                growth_rate="medium",
                evergreen=True,
                roles=["accent", "edge"],
                style_tags=["cottage", "farmhouse", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "gray-green foliage",
                    "summer": "purple flower spikes",
                    "fall": "gray-green foliage",
                    "winter": "semi-evergreen structure"
                },
                fragrant=True,
                notes="Requires excellent drainage, pollinator magnet"
            ),

            Plant(
                common_name="Russian Sage",
                botanical_name="Perovskia atriplicifolia",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "sand"],
                mature_height_ft=4.0,
                mature_width_ft=3.0,
                form="upright",
                growth_rate="medium",
                evergreen=False,
                roles=["accent"],
                style_tags=["modern", "naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "silvery foliage emerging",
                    "summer": "lavender-blue flower spikes",
                    "fall": "continued blooming",
                    "winter": "silver stems"
                },
                fragrant=True,
                notes="Extremely heat and drought tolerant, attracts pollinators"
            ),

            Plant(
                common_name="Butterfly Bush",
                botanical_name="Buddleia davidii",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=8.0,
                mature_width_ft=6.0,
                form="vase",
                growth_rate="fast",
                evergreen=False,
                roles=["accent"],
                style_tags=["cottage", "naturalistic", "farmhouse"],
                maintenance_level="medium",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "rapid regrowth",
                    "summer": "fragrant flower panicles",
                    "fall": "continued blooming",
                    "winter": "none (cut back)"
                },
                fragrant=True,
                notes="Major butterfly and pollinator attractor, cut back hard annually"
            ),

            Plant(
                common_name="Coneflower",
                botanical_name="Echinacea purpurea",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=3.0,
                mature_width_ft=2.0,
                form="upright",
                growth_rate="medium",
                evergreen=False,
                roles=["accent"],
                style_tags=["naturalistic", "farmhouse", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["central and eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "basal foliage",
                    "summer": "purple daisy flowers",
                    "fall": "seed heads for birds",
                    "winter": "architectural seed heads"
                },
                notes="Native, drought tolerant, excellent for wildlife"
            ),

            Plant(
                common_name="Black-Eyed Susan",
                botanical_name="Rudbeckia fulgida",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=2.5,
                mature_width_ft=2.0,
                form="upright",
                growth_rate="fast",
                evergreen=False,
                roles=["accent"],
                style_tags=["naturalistic", "farmhouse", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "basal foliage",
                    "summer": "golden yellow flowers",
                    "fall": "continued blooming, seed heads",
                    "winter": "seed heads"
                },
                notes="Bulletproof native perennial, spreads readily"
            ),

            Plant(
                common_name="Ornamental Grass - Maiden",
                botanical_name="Miscanthus sinensis",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=6.0,
                mature_width_ft=4.0,
                form="fountain",
                growth_rate="fast",
                evergreen=False,
                roles=["accent", "structural"],
                style_tags=["modern", "naturalistic", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "emerging green blades",
                    "summer": "graceful green foliage",
                    "fall": "plumes, golden color",
                    "winter": "tan architectural presence"
                },
                notes="Dramatic movement and texture, cut back in late winter"
            ),

            Plant(
                common_name="Ornamental Grass - Fountain",
                botanical_name="Pennisetum alopecuroides",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=3.0,
                mature_width_ft=3.0,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["accent", "edge"],
                style_tags=["modern", "naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "emerging green",
                    "summer": "fuzzy flower heads",
                    "fall": "golden foliage",
                    "winter": "tan structure"
                },
                notes="Compact fountain grass, great border accent"
            ),

            Plant(
                common_name="Switchgrass",
                botanical_name="Panicum virgatum",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry", "average", "wet"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=5.0,
                mature_width_ft=3.0,
                form="upright",
                growth_rate="fast",
                evergreen=False,
                roles=["accent", "screening"],
                style_tags=["naturalistic", "modern", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["throughout US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "blue-green foliage",
                    "summer": "airy flower panicles",
                    "fall": "golden/red fall color",
                    "winter": "tan winter presence"
                },
                notes="Native prairie grass, extremely adaptable"
            ),

            Plant(
                common_name="Daylily",
                botanical_name="Hemerocallis spp.",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=2.5,
                mature_width_ft=2.5,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["accent", "edge"],
                style_tags=["traditional", "cottage", "farmhouse"],
                maintenance_level="low",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "grassy foliage",
                    "summer": "trumpet flowers",
                    "fall": "reblooming varieties",
                    "winter": "dormant"
                },
                notes="Extremely tough, many color options available"
            ),

            Plant(
                common_name="Hosta",
                botanical_name="Hosta spp.",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam"],
                mature_height_ft=2.0,
                mature_width_ft=3.0,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["accent", "groundcover"],
                style_tags=["traditional", "cottage", "naturalistic"],
                maintenance_level="low",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "unfurling leaves",
                    "summer": "bold foliage, flower spikes",
                    "fall": "golden foliage",
                    "winter": "dormant"
                },
                notes="Premier shade perennial, many varieties available"
            ),

            Plant(
                common_name="Azalea",
                botanical_name="Rhododendron spp.",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=5.0,
                mature_width_ft=5.0,
                form="mounding",
                growth_rate="slow",
                evergreen=True,
                roles=["accent", "foundation"],
                style_tags=["traditional", "cottage", "craftsman"],
                maintenance_level="medium",
                deer_resistant=False,
                seasonal_interest={
                    "spring": "profuse flowers",
                    "summer": "evergreen foliage",
                    "fall": "evergreen foliage",
                    "winter": "evergreen structure"
                },
                notes="Classic spring bloomer, needs acidic soil"
            ),

            Plant(
                common_name="Rhododendron",
                botanical_name="Rhododendron catawbiense",
                zone_min=4,
                zone_max=8,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=8.0,
                mature_width_ft=8.0,
                form="rounded",
                growth_rate="slow",
                evergreen=True,
                roles=["accent", "structural", "screening"],
                style_tags=["traditional", "craftsman", "naturalistic"],
                maintenance_level="medium",
                deer_resistant=False,
                native_regions=["eastern US"],
                seasonal_interest={
                    "spring": "large flower clusters",
                    "summer": "bold evergreen foliage",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Native, needs acidic soil and protected location"
            ),

            # ================================================================
            # SCREENING PLANTS
            # ================================================================
            Plant(
                common_name="Green Giant Arborvitae",
                botanical_name="Thuja 'Green Giant'",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=40.0,
                mature_width_ft=12.0,
                form="pyramidal",
                growth_rate="fast",
                evergreen=True,
                roles=["screening", "canopy"],
                style_tags=["traditional", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "fresh green growth",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Fast-growing screen, deer resistant unlike other arborvitae"
            ),

            Plant(
                common_name="Leyland Cypress",
                botanical_name="x Cuprocyparis leylandii",
                zone_min=6,
                zone_max=10,
                sun_tolerance=["full"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=50.0,
                mature_width_ft=15.0,
                form="columnar",
                growth_rate="fast",
                evergreen=True,
                roles=["screening"],
                style_tags=["traditional"],
                maintenance_level="medium",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Very fast screen, susceptible to disease, short-lived"
            ),

            Plant(
                common_name="Nellie R. Stevens Holly",
                botanical_name="Ilex x 'Nellie R. Stevens'",
                zone_min=6,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=20.0,
                mature_width_ft=10.0,
                form="pyramidal",
                growth_rate="medium",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["traditional", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "inconspicuous flowers",
                    "summer": "dark green foliage",
                    "fall": "red berries",
                    "winter": "red berries, evergreen"
                },
                notes="Reliable screen, produces berries without male pollinator nearby"
            ),

            Plant(
                common_name="American Holly",
                botanical_name="Ilex opaca",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=30.0,
                mature_width_ft=15.0,
                form="pyramidal",
                growth_rate="slow",
                evergreen=True,
                roles=["screening", "canopy"],
                style_tags=["traditional", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "new growth",
                    "summer": "spiny evergreen foliage",
                    "fall": "red berries",
                    "winter": "red berries, evergreen"
                },
                notes="Native, needs male/female for berries, classic holiday plant"
            ),

            Plant(
                common_name="Wax Myrtle",
                botanical_name="Myrica cerifera",
                zone_min=7,
                zone_max=11,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry", "average", "wet"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=15.0,
                mature_width_ft=10.0,
                form="upright",
                growth_rate="fast",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                salt_tolerant=True,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "aromatic foliage",
                    "summer": "evergreen structure",
                    "fall": "waxy gray berries",
                    "winter": "evergreen structure"
                },
                fragrant=True,
                notes="Extremely tough native, fixes nitrogen, bayberry scent"
            ),

            Plant(
                common_name="Skip Laurel",
                botanical_name="Prunus laurocerasus 'Schipkaensis'",
                zone_min=6,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=10.0,
                mature_width_ft=6.0,
                form="upright",
                growth_rate="medium",
                evergreen=True,
                roles=["screening", "structural"],
                style_tags=["traditional", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "fragrant white flowers",
                    "summer": "glossy green foliage",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                fragrant=True,
                notes="Cold-hardy laurel, good urban tolerance"
            ),

            Plant(
                common_name="Eastern Red Cedar",
                botanical_name="Juniperus virginiana",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand", "rocky"],
                mature_height_ft=40.0,
                mature_width_ft=15.0,
                form="columnar",
                growth_rate="medium",
                evergreen=True,
                roles=["screening", "canopy"],
                style_tags=["naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "blue-green foliage",
                    "fall": "blue berries",
                    "winter": "evergreen structure, wildlife cover"
                },
                notes="Extremely adaptable native, excellent wildlife habitat"
            ),

            Plant(
                common_name="Viburnum - Arrowwood",
                botanical_name="Viburnum dentatum",
                zone_min=3,
                zone_max=8,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=10.0,
                mature_width_ft=8.0,
                form="rounded",
                growth_rate="medium",
                evergreen=False,
                roles=["screening", "structural"],
                style_tags=["naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "white flower clusters",
                    "summer": "blue-black berries",
                    "fall": "red/purple foliage",
                    "winter": "architectural branching"
                },
                notes="Native powerhouse, four-season interest, bird magnet"
            ),

            Plant(
                common_name="Clumping Bamboo",
                botanical_name="Bambusa multiplex",
                zone_min=8,
                zone_max=10,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=20.0,
                mature_width_ft=8.0,
                form="upright",
                growth_rate="fast",
                evergreen=True,
                roles=["screening"],
                style_tags=["modern"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "new culm emergence",
                    "summer": "graceful foliage",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Non-invasive clumping type, provides quick privacy"
            ),

            # ================================================================
            # FOUNDATION SOFTENERS
            # ================================================================
            Plant(
                common_name="Dwarf Boxwood",
                botanical_name="Buxus sempervirens 'Suffruticosa'",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=2.0,
                mature_width_ft=2.0,
                form="rounded",
                growth_rate="slow",
                evergreen=True,
                roles=["foundation", "edge"],
                style_tags=["traditional", "modern"],
                maintenance_level="medium",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Classic low hedge, edging, or foundation plant"
            ),

            Plant(
                common_name="Spiraea",
                botanical_name="Spiraea japonica",
                zone_min=4,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=3.0,
                mature_width_ft=3.0,
                form="mounding",
                growth_rate="medium",
                evergreen=False,
                roles=["foundation", "accent"],
                style_tags=["traditional", "cottage", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "pink flower clusters",
                    "summer": "continued blooming",
                    "fall": "reddish fall color",
                    "winter": "fine-textured branching"
                },
                notes="Tough, floriferous, many cultivar options"
            ),

            Plant(
                common_name="Abelia",
                botanical_name="Abelia x grandiflora",
                zone_min=6,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=4.0,
                mature_width_ft=4.0,
                form="mounding",
                growth_rate="medium",
                evergreen=True,
                roles=["foundation", "accent"],
                style_tags=["traditional", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "new bronze growth",
                    "summer": "white/pink flowers, butterflies",
                    "fall": "bronze-purple foliage",
                    "winter": "semi-evergreen structure"
                },
                fragrant=True,
                notes="Long bloom season, excellent butterfly plant"
            ),

            Plant(
                common_name="Nandina",
                botanical_name="Nandina domestica",
                zone_min=6,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=5.0,
                mature_width_ft=3.0,
                form="upright",
                growth_rate="medium",
                evergreen=True,
                roles=["foundation", "accent"],
                style_tags=["modern", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "white flower panicles",
                    "summer": "fine-textured foliage",
                    "fall": "red berries, red foliage",
                    "winter": "red berries, red/bronze foliage"
                },
                notes="Four-season color, many dwarf cultivars available"
            ),

            Plant(
                common_name="Compact Oregon Grape",
                botanical_name="Mahonia aquifolium 'Compacta'",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=3.0,
                mature_width_ft=3.0,
                form="mounding",
                growth_rate="slow",
                evergreen=True,
                roles=["foundation"],
                style_tags=["naturalistic", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["western US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "yellow flower clusters",
                    "summer": "blue berries",
                    "fall": "evergreen holly-like foliage",
                    "winter": "bronze-red foliage"
                },
                notes="Native, shade-tolerant, unique texture"
            ),

            Plant(
                common_name="Distylium",
                botanical_name="Distylium 'Swing Low'",
                zone_min=7,
                zone_max=9,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=2.0,
                mature_width_ft=4.0,
                form="spreading",
                growth_rate="slow",
                evergreen=True,
                roles=["foundation", "groundcover"],
                style_tags=["modern", "traditional"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "red flowers",
                    "summer": "blue-green foliage",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Extremely tough, boxwood alternative, no pest issues"
            ),

            # ================================================================
            # GROUNDCOVERS
            # ================================================================
            Plant(
                common_name="Liriope",
                botanical_name="Liriope muscari",
                zone_min=5,
                zone_max=10,
                sun_tolerance=["full", "part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay", "sand"],
                mature_height_ft=1.0,
                mature_width_ft=1.5,
                form="mounding",
                growth_rate="medium",
                evergreen=True,
                roles=["groundcover", "edge"],
                style_tags=["traditional", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "fresh green foliage",
                    "summer": "purple flower spikes",
                    "fall": "black berries",
                    "winter": "evergreen structure"
                },
                notes="Extremely adaptable, tolerates dry shade"
            ),

            Plant(
                common_name="Mondo Grass",
                botanical_name="Ophiopogon japonicus",
                zone_min=6,
                zone_max=10,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=0.5,
                mature_width_ft=1.0,
                form="mounding",
                growth_rate="slow",
                evergreen=True,
                roles=["groundcover", "edge"],
                style_tags=["modern", "traditional"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "evergreen structure",
                    "summer": "small white flowers",
                    "fall": "blue berries",
                    "winter": "evergreen structure"
                },
                notes="Fine texture, excellent between pavers or as edging"
            ),

            Plant(
                common_name="Creeping Juniper",
                botanical_name="Juniperus horizontalis",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "sand", "rocky"],
                mature_height_ft=0.5,
                mature_width_ft=8.0,
                form="spreading",
                growth_rate="medium",
                evergreen=True,
                roles=["groundcover"],
                style_tags=["modern", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["northern US"],
                seasonal_interest={
                    "spring": "blue-green foliage",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "plum-tinted foliage"
                },
                notes="Excellent for slopes and erosion control, very tough"
            ),

            Plant(
                common_name="Pachysandra",
                botanical_name="Pachysandra terminalis",
                zone_min=4,
                zone_max=8,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=0.75,
                mature_width_ft=1.5,
                form="spreading",
                growth_rate="medium",
                evergreen=True,
                roles=["groundcover"],
                style_tags=["traditional"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "white flower spikes",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Classic shade groundcover, spreads readily"
            ),

            Plant(
                common_name="Vinca",
                botanical_name="Vinca minor",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=0.5,
                mature_width_ft=2.0,
                form="spreading",
                growth_rate="fast",
                evergreen=True,
                roles=["groundcover"],
                style_tags=["traditional", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "blue-violet flowers",
                    "summer": "evergreen structure",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Aggressive spreader, excellent erosion control"
            ),

            Plant(
                common_name="Ajuga",
                botanical_name="Ajuga reptans",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=0.5,
                mature_width_ft=1.5,
                form="spreading",
                growth_rate="fast",
                evergreen=True,
                roles=["groundcover"],
                style_tags=["cottage", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "blue flower spikes",
                    "summer": "bronze/purple foliage",
                    "fall": "evergreen foliage",
                    "winter": "evergreen structure"
                },
                notes="Colorful foliage options, spreads quickly"
            ),

            Plant(
                common_name="Sedum - Groundcover",
                botanical_name="Sedum spurium",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["dry"],
                soil_tolerance=["loam", "sand", "rocky"],
                mature_height_ft=0.5,
                mature_width_ft=2.0,
                form="spreading",
                growth_rate="medium",
                evergreen=True,
                roles=["groundcover"],
                style_tags=["modern", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                wildlife_value=True,
                seasonal_interest={
                    "spring": "succulent rosettes",
                    "summer": "pink flower clusters",
                    "fall": "burgundy foliage",
                    "winter": "semi-evergreen"
                },
                notes="Extremely drought tolerant, excellent for poor soils"
            ),

            Plant(
                common_name="Native Fern - Christmas",
                botanical_name="Polystichum acrostichoides",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=2.0,
                mature_width_ft=2.0,
                form="mounding",
                growth_rate="slow",
                evergreen=True,
                roles=["groundcover", "accent"],
                style_tags=["naturalistic", "cottage", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                seasonal_interest={
                    "spring": "fiddlehead emergence",
                    "summer": "dark green fronds",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure"
                },
                notes="Native evergreen fern, excellent texture"
            ),

            # ================================================================
            # CANOPY TREES
            # ================================================================
            Plant(
                common_name="Red Maple",
                botanical_name="Acer rubrum",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=50.0,
                mature_width_ft=35.0,
                form="rounded",
                growth_rate="fast",
                evergreen=False,
                roles=["canopy"],
                style_tags=["traditional", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "red flowers before leaves",
                    "summer": "green canopy",
                    "fall": "brilliant red foliage",
                    "winter": "gray bark structure"
                },
                notes="Native, adaptable, excellent fall color"
            ),

            Plant(
                common_name="White Oak",
                botanical_name="Quercus alba",
                zone_min=3,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=80.0,
                mature_width_ft=80.0,
                form="broad",
                growth_rate="slow",
                evergreen=False,
                roles=["canopy"],
                style_tags=["traditional", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "new leaves with pink tinge",
                    "summer": "deep green canopy",
                    "fall": "wine-red to brown foliage",
                    "winter": "impressive branching structure"
                },
                notes="Long-lived native, keystone wildlife species"
            ),

            Plant(
                common_name="Willow Oak",
                botanical_name="Quercus phellos",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=60.0,
                mature_width_ft=40.0,
                form="pyramidal",
                growth_rate="fast",
                evergreen=False,
                roles=["canopy"],
                style_tags=["traditional", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "willow-like new leaves",
                    "summer": "fine-textured canopy",
                    "fall": "yellow to russet",
                    "winter": "pyramidal form"
                },
                notes="Fast-growing native oak, fine texture"
            ),

            Plant(
                common_name="Sweetgum",
                botanical_name="Liquidambar styraciflua",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=60.0,
                mature_width_ft=40.0,
                form="pyramidal",
                growth_rate="medium",
                evergreen=False,
                roles=["canopy"],
                style_tags=["naturalistic"],
                maintenance_level="medium",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "star-shaped leaves emerging",
                    "summer": "glossy green canopy",
                    "fall": "spectacular multi-colored fall",
                    "winter": "spiky seed balls, corky bark"
                },
                notes="Native, incredible fall color, messy seed balls"
            ),

            Plant(
                common_name="Tulip Poplar",
                botanical_name="Liriodendron tulipifera",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=80.0,
                mature_width_ft=40.0,
                form="pyramidal",
                growth_rate="fast",
                evergreen=False,
                roles=["canopy"],
                style_tags=["naturalistic", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "tulip-shaped flowers",
                    "summer": "unique leaf shape, shade",
                    "fall": "golden yellow",
                    "winter": "straight trunk structure"
                },
                notes="Tall native, fast growing, unique leaf shape"
            ),

            Plant(
                common_name="Live Oak",
                botanical_name="Quercus virginiana",
                zone_min=7,
                zone_max=10,
                sun_tolerance=["full"],
                water_tolerance=["dry", "average"],
                soil_tolerance=["loam", "sand"],
                mature_height_ft=50.0,
                mature_width_ft=80.0,
                form="broad",
                growth_rate="medium",
                evergreen=True,
                roles=["canopy"],
                style_tags=["traditional", "naturalistic"],
                maintenance_level="low",
                deer_resistant=True,
                salt_tolerant=True,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "brief leaf drop, new growth",
                    "summer": "dense evergreen shade",
                    "fall": "evergreen structure",
                    "winter": "evergreen structure, spreading form"
                },
                notes="Iconic southern tree, massive spreading canopy"
            ),

            Plant(
                common_name="Bald Cypress",
                botanical_name="Taxodium distichum",
                zone_min=4,
                zone_max=10,
                sun_tolerance=["full"],
                water_tolerance=["average", "wet"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=60.0,
                mature_width_ft=25.0,
                form="pyramidal",
                growth_rate="medium",
                evergreen=False,
                roles=["canopy"],
                style_tags=["naturalistic", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "feathery new foliage",
                    "summer": "fine-textured green canopy",
                    "fall": "rusty orange/bronze",
                    "winter": "impressive trunk structure"
                },
                notes="Native, tolerates wet and dry, long-lived"
            ),

            # ================================================================
            # UNDERSTORY TREES
            # ================================================================
            Plant(
                common_name="Dogwood",
                botanical_name="Cornus florida",
                zone_min=5,
                zone_max=9,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=25.0,
                mature_width_ft=25.0,
                form="layered",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["traditional", "naturalistic", "craftsman"],
                maintenance_level="medium",
                deer_resistant=False,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "white/pink bracts",
                    "summer": "horizontal branching",
                    "fall": "red berries, red foliage",
                    "winter": "beautiful branching structure"
                },
                notes="Classic native understory, four-season beauty"
            ),

            Plant(
                common_name="Kousa Dogwood",
                botanical_name="Cornus kousa",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=20.0,
                mature_width_ft=20.0,
                form="vase",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["craftsman", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "pointed white bracts",
                    "summer": "exfoliating bark",
                    "fall": "red berries, red foliage",
                    "winter": "mottled bark"
                },
                notes="Disease-resistant alternative to native dogwood"
            ),

            Plant(
                common_name="Redbud",
                botanical_name="Cercis canadensis",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=25.0,
                mature_width_ft=25.0,
                form="vase",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["naturalistic", "farmhouse", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "magenta-pink flowers on bare branches",
                    "summer": "heart-shaped leaves",
                    "fall": "yellow foliage",
                    "winter": "zigzag branching"
                },
                notes="Native, early spring color, heart-shaped leaves"
            ),

            Plant(
                common_name="Serviceberry",
                botanical_name="Amelanchier x grandiflora",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=20.0,
                mature_width_ft=15.0,
                form="vase",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["naturalistic", "farmhouse", "craftsman"],
                maintenance_level="low",
                deer_resistant=False,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "white flowers",
                    "summer": "edible blue berries",
                    "fall": "orange-red foliage",
                    "winter": "smooth gray bark"
                },
                notes="Native, multi-season interest, edible berries"
            ),

            Plant(
                common_name="Crape Myrtle",
                botanical_name="Lagerstroemia indica",
                zone_min=6,
                zone_max=10,
                sun_tolerance=["full"],
                water_tolerance=["average"],
                soil_tolerance=["loam", "clay"],
                mature_height_ft=20.0,
                mature_width_ft=15.0,
                form="vase",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["traditional", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "new growth",
                    "summer": "long-lasting flower clusters",
                    "fall": "orange-red foliage",
                    "winter": "exfoliating bark"
                },
                notes="Southern classic, long summer bloom, choose disease-resistant cultivars"
            ),

            Plant(
                common_name="Japanese Stewartia",
                botanical_name="Stewartia pseudocamellia",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=25.0,
                mature_width_ft=20.0,
                form="pyramidal",
                growth_rate="slow",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["craftsman", "modern"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "emerging foliage",
                    "summer": "camellia-like white flowers",
                    "fall": "orange-red-purple foliage",
                    "winter": "exfoliating bark"
                },
                notes="Four-season specimen, stunning bark"
            ),

            Plant(
                common_name="Witch Hazel",
                botanical_name="Hamamelis x intermedia",
                zone_min=5,
                zone_max=8,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=15.0,
                mature_width_ft=15.0,
                form="vase",
                growth_rate="medium",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["naturalistic", "cottage", "craftsman"],
                maintenance_level="low",
                deer_resistant=True,
                seasonal_interest={
                    "spring": "emerging foliage",
                    "summer": "coarse-textured foliage",
                    "fall": "yellow fall color",
                    "winter": "fragrant yellow/orange flowers"
                },
                fragrant=True,
                notes="Winter-blooming, fragrant, unique seasonal interest"
            ),

            Plant(
                common_name="Carolina Silverbell",
                botanical_name="Halesia tetraptera",
                zone_min=4,
                zone_max=8,
                sun_tolerance=["part", "shade"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=30.0,
                mature_width_ft=25.0,
                form="rounded",
                growth_rate="medium",
                evergreen=False,
                roles=["understory"],
                style_tags=["naturalistic", "cottage"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["southeastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "white bell-shaped flowers",
                    "summer": "clean green foliage",
                    "fall": "yellow foliage",
                    "winter": "winged seed pods"
                },
                notes="Native, delicate spring flowers, underused"
            ),

            Plant(
                common_name="Fringetree",
                botanical_name="Chionanthus virginicus",
                zone_min=4,
                zone_max=9,
                sun_tolerance=["full", "part"],
                water_tolerance=["average"],
                soil_tolerance=["loam"],
                mature_height_ft=20.0,
                mature_width_ft=20.0,
                form="rounded",
                growth_rate="slow",
                evergreen=False,
                roles=["understory", "accent"],
                style_tags=["naturalistic", "cottage", "farmhouse"],
                maintenance_level="low",
                deer_resistant=True,
                native_regions=["eastern US"],
                wildlife_value=True,
                seasonal_interest={
                    "spring": "fragrant white fringe-like flowers",
                    "summer": "blue berries on female",
                    "fall": "bright yellow foliage",
                    "winter": "gray bark"
                },
                fragrant=True,
                notes="Native, fragrant flowers, excellent specimen"
            ),
        ]

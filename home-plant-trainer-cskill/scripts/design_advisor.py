"""
Design Advisor Module for Home Plant Trainer

Provides style-specific design guidance, plant palette creation,
and AI prompt generation for residential landscape design.

This module integrates the training dataset principles from:
- Better Homes & Gardens
- Sunset Magazine
- Houzz
- Yardzen
- Professional landscape design philosophy
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class DesignPrinciple(Enum):
    """Core design principles for residential landscapes"""
    FRAMING = "framing"
    LAYERING = "layering"
    RHYTHM = "rhythm"
    BALANCE = "balance"
    SYMMETRY = "symmetry"
    REPETITION = "repetition"
    SCREENING = "screening"
    FLOW = "flow"
    COHESION = "cohesion"
    INTEGRATION = "integration"


class SeasonalInterest(Enum):
    """Seasonal interest categories"""
    SPRING_BLOOM = "spring_bloom"
    SUMMER_BLOOM = "summer_bloom"
    FALL_COLOR = "fall_color"
    WINTER_STRUCTURE = "winter_structure"
    YEAR_ROUND = "year_round"
    EVERGREEN_BACKBONE = "evergreen_backbone"


@dataclass
class DesignPackage:
    """A complete design package for a style"""
    style_name: str
    principles: List[DesignPrinciple]
    plant_count_target: Dict[str, int]  # role -> count
    layer_priority: List[str]
    spacing_approach: str
    color_palette: List[str]
    texture_mix: str
    seasonal_priorities: List[SeasonalInterest]
    design_tips: List[str]
    avoid_list: List[str]


class ResidentialDesignAdvisor:
    """
    Design advisor for residential plant landscapes.

    Provides style guidance, palette creation, and design
    recommendations based on professional landscape principles.
    """

    # Design packages for each style
    DESIGN_PACKAGES = {
        "traditional": DesignPackage(
            style_name="Traditional / Colonial",
            principles=[
                DesignPrinciple.SYMMETRY,
                DesignPrinciple.BALANCE,
                DesignPrinciple.FRAMING
            ],
            plant_count_target={
                "structural": 4,
                "accent": 2,
                "foundation_softener": 6,
                "edge_border": 8,
                "groundcover": 12
            },
            layer_priority=["shrub", "groundcover", "herbaceous"],
            spacing_approach="formal_geometric",
            color_palette=["deep_green", "white", "pink", "red", "burgundy"],
            texture_mix="fine_to_medium",
            seasonal_priorities=[
                SeasonalInterest.EVERGREEN_BACKBONE,
                SeasonalInterest.SPRING_BLOOM
            ],
            design_tips=[
                "Mirror plantings on either side of entry",
                "Use clipped hedges for formal lines",
                "Limit species variety for cohesion",
                "Frame architectural features with plants",
                "Maintain clean, defined bed edges"
            ],
            avoid_list=[
                "Overly casual or naturalistic groupings",
                "Mixed textures that clash",
                "Asymmetrical plantings near entry",
                "Wildflower or meadow aesthetics"
            ]
        ),

        "farmhouse": DesignPackage(
            style_name="Farmhouse",
            principles=[
                DesignPrinciple.FLOW,
                DesignPrinciple.RHYTHM,
                DesignPrinciple.COHESION
            ],
            plant_count_target={
                "structural": 3,
                "accent": 5,
                "foundation_softener": 4,
                "edge_border": 10,
                "groundcover": 15
            },
            layer_priority=["shrub", "herbaceous", "groundcover"],
            spacing_approach="informal_clustered",
            color_palette=["soft_green", "white", "lavender", "pink", "yellow", "blue"],
            texture_mix="mixed_naturalistic",
            seasonal_priorities=[
                SeasonalInterest.SPRING_BLOOM,
                SeasonalInterest.SUMMER_BLOOM,
                SeasonalInterest.FALL_COLOR
            ],
            design_tips=[
                "Group plants in odd numbers (3, 5, 7)",
                "Allow plants to grow naturally with minimal shaping",
                "Mix flowering shrubs with perennials",
                "Include native species for authenticity",
                "Create gentle curves in bed lines"
            ],
            avoid_list=[
                "Highly formal or clipped hedges",
                "Rigid geometric layouts",
                "Exotic tropical plants",
                "Excessive ornamentation"
            ]
        ),

        "craftsman": DesignPackage(
            style_name="Craftsman",
            principles=[
                DesignPrinciple.LAYERING,
                DesignPrinciple.INTEGRATION,
                DesignPrinciple.RHYTHM
            ],
            plant_count_target={
                "structural": 5,
                "accent": 3,
                "foundation_softener": 5,
                "edge_border": 6,
                "groundcover": 10
            },
            layer_priority=["shrub", "understory", "groundcover"],
            spacing_approach="layered_horizontal",
            color_palette=["forest_green", "bronze", "rust", "gold", "cream", "burgundy"],
            texture_mix="medium_to_bold",
            seasonal_priorities=[
                SeasonalInterest.EVERGREEN_BACKBONE,
                SeasonalInterest.FALL_COLOR,
                SeasonalInterest.WINTER_STRUCTURE
            ],
            design_tips=[
                "Layer plants front-to-back by height",
                "Use evergreens as the backbone",
                "Echo natural materials (stone, wood) with plant colors",
                "Create strong horizontal lines with spreading forms",
                "Emphasize entry with specimen plants"
            ],
            avoid_list=[
                "Vertical or columnar forms only",
                "Sparse, minimalist plantings",
                "Tropical or exotic species",
                "High-contrast color schemes"
            ]
        ),

        "modern": DesignPackage(
            style_name="Modern / Contemporary",
            principles=[
                DesignPrinciple.REPETITION,
                DesignPrinciple.BALANCE,
                DesignPrinciple.COHESION
            ],
            plant_count_target={
                "structural": 3,
                "accent": 2,
                "foundation_softener": 3,
                "edge_border": 5,
                "groundcover": 8
            },
            layer_priority=["shrub", "groundcover"],
            spacing_approach="geometric_minimal",
            color_palette=["dark_green", "silver", "burgundy", "white", "black", "chartreuse"],
            texture_mix="bold_architectural",
            seasonal_priorities=[
                SeasonalInterest.YEAR_ROUND,
                SeasonalInterest.EVERGREEN_BACKBONE
            ],
            design_tips=[
                "Limit plant palette to 3-5 species maximum",
                "Use mass plantings of single species",
                "Select plants with strong architectural form",
                "Create negative space intentionally",
                "Repeat plant groupings for rhythm"
            ],
            avoid_list=[
                "Cottage-style mixed borders",
                "Too many flowering species",
                "Naturalistic or wild aesthetics",
                "Fussy or high-maintenance plants"
            ]
        ),

        "cottage": DesignPackage(
            style_name="Cottage Garden",
            principles=[
                DesignPrinciple.FLOW,
                DesignPrinciple.LAYERING,
                DesignPrinciple.RHYTHM
            ],
            plant_count_target={
                "structural": 4,
                "accent": 8,
                "foundation_softener": 4,
                "edge_border": 12,
                "groundcover": 10
            },
            layer_priority=["herbaceous", "shrub", "groundcover"],
            spacing_approach="dense_informal",
            color_palette=["pink", "purple", "blue", "white", "soft_yellow", "lavender"],
            texture_mix="mixed_abundant",
            seasonal_priorities=[
                SeasonalInterest.SPRING_BLOOM,
                SeasonalInterest.SUMMER_BLOOM,
                SeasonalInterest.FALL_COLOR
            ],
            design_tips=[
                "Plant densely for lush, abundant effect",
                "Mix heights within the same bed",
                "Include self-seeding perennials",
                "Allow plants to spill over edges",
                "Plan for continuous bloom succession"
            ],
            avoid_list=[
                "Sparse, minimalist plantings",
                "Rigid geometric layouts",
                "Highly clipped or formal hedges",
                "Large expanses of bare mulch"
            ]
        ),

        "naturalistic": DesignPackage(
            style_name="Naturalistic / Native",
            principles=[
                DesignPrinciple.FLOW,
                DesignPrinciple.COHESION,
                DesignPrinciple.INTEGRATION
            ],
            plant_count_target={
                "structural": 3,
                "accent": 6,
                "foundation_softener": 3,
                "edge_border": 8,
                "groundcover": 20
            },
            layer_priority=["herbaceous", "shrub", "groundcover", "canopy"],
            spacing_approach="naturalized_drifts",
            color_palette=["varied_green", "gold", "purple", "white", "orange", "native_mix"],
            texture_mix="natural_varied",
            seasonal_priorities=[
                SeasonalInterest.SUMMER_BLOOM,
                SeasonalInterest.FALL_COLOR,
                SeasonalInterest.WINTER_STRUCTURE
            ],
            design_tips=[
                "Prioritize native species for the region",
                "Plant in naturalized drifts, not rows",
                "Include plants for pollinators and wildlife",
                "Allow seed heads to persist for winter interest",
                "Embrace seasonal change and natural cycles"
            ],
            avoid_list=[
                "Non-native invasive species",
                "Highly formal or geometric layouts",
                "Excessive pruning or shaping",
                "Plants requiring high water or fertilizer"
            ]
        )
    }

    @classmethod
    def get_design_package(cls, style: str) -> DesignPackage:
        """Get the design package for a style"""
        return cls.DESIGN_PACKAGES.get(
            style.lower(),
            cls.DESIGN_PACKAGES["traditional"]
        )

    @classmethod
    def generate_design_brief(
        cls,
        style: str,
        space: str,
        zone: int,
        sun: str,
        water: str
    ) -> Dict[str, Any]:
        """
        Generate a complete design brief for a project.

        Args:
            style: Design style
            space: Yard space (front_yard, backyard, side_yard)
            zone: USDA zone
            sun: Sun exposure
            water: Water profile

        Returns:
            Complete design brief with guidance
        """
        package = cls.get_design_package(style)

        brief = {
            "project": {
                "style": package.style_name,
                "space": space.replace("_", " ").title(),
                "zone": zone,
                "conditions": {
                    "sun": sun,
                    "water": water
                }
            },
            "design_direction": {
                "principles": [p.value for p in package.principles],
                "spacing_approach": package.spacing_approach,
                "color_palette": package.color_palette,
                "texture_approach": package.texture_mix
            },
            "plant_targets": package.plant_count_target,
            "layer_priority": package.layer_priority,
            "seasonal_focus": [s.value for s in package.seasonal_priorities],
            "design_tips": package.design_tips,
            "avoid": package.avoid_list,
            "generated": datetime.now().isoformat()
        }

        return brief

    @classmethod
    def get_style_comparison(cls) -> Dict[str, Dict]:
        """Get comparison of all available styles"""
        comparison = {}

        for style_key, package in cls.DESIGN_PACKAGES.items():
            comparison[style_key] = {
                "name": package.style_name,
                "key_principles": [p.value for p in package.principles[:2]],
                "spacing": package.spacing_approach,
                "texture": package.texture_mix,
                "best_for": cls._get_best_for(style_key)
            }

        return comparison

    @classmethod
    def _get_best_for(cls, style: str) -> List[str]:
        """Get 'best for' descriptions for each style"""
        best_for = {
            "traditional": [
                "Colonial and Georgian homes",
                "Formal entryways",
                "Classic curb appeal"
            ],
            "farmhouse": [
                "Country and rural settings",
                "Relaxed outdoor living",
                "Native plant enthusiasts"
            ],
            "craftsman": [
                "Bungalow and Arts & Crafts homes",
                "Mountain or woodland settings",
                "Four-season interest"
            ],
            "modern": [
                "Contemporary architecture",
                "Low-maintenance preference",
                "Minimalist aesthetic"
            ],
            "cottage": [
                "Romantic garden lovers",
                "Abundant bloom desired",
                "English garden style"
            ],
            "naturalistic": [
                "Eco-conscious homeowners",
                "Wildlife habitat creation",
                "Low-input landscapes"
            ]
        }
        return best_for.get(style, ["General residential use"])


class AIPromptGenerator:
    """
    Generate AI prompts for plant design tasks.

    These prompts can be used with AI assistants to generate
    plant recommendations, swap alternatives, and design validations.
    """

    @staticmethod
    def build_package_prompt(
        style: str,
        space: str,
        zone: int,
        sun: str,
        water: str,
        height_limit: float = 20.0,
        width_limit: float = 10.0
    ) -> str:
        """
        Generate prompt for creating a plant package.

        Returns:
            Formatted prompt string
        """
        return f"""You are a residential plant designer. Output plant-only designs. Never suggest hardscape.

Create a {style} residential planting plan for a {space.replace('_', ' ')}.

Constraints:
- Zone: {zone}
- Sun exposure: {sun}
- Water profile: {water}
- Height limit: {height_limit} ft
- Width limit: {width_limit} ft

Required elements:
1. Structural backbone plants (evergreen preferred)
2. Accent layer for seasonal interest
3. Groundcover massing for cohesion

Return:
- Role-based plant list with botanical and common names
- Spacing concept for each layer
- Seasonal interest summary (spring, summer, fall, winter)
- Maintenance notes for homeowner

Focus on plants that work well together and create a cohesive design."""

    @staticmethod
    def swap_plant_prompt(
        plant_name: str,
        role: str,
        zone: int,
        sun: str,
        water: str,
        height_limit: float,
        width_limit: float
    ) -> str:
        """
        Generate prompt for finding plant alternatives.

        Returns:
            Formatted prompt string
        """
        return f"""Swap this plant: {plant_name}
Keep the same role: {role}

Site constraints:
- Zone: {zone}
- Sun: {sun}
- Water: {water}
- Size maximum: {height_limit}ft height x {width_limit}ft width

Return 3 alternatives ranked best-to-worst with:
1. Botanical name and common name
2. Why it works as a swap (zone tolerance, habit match, etc.)
3. Any differences from the original to note
4. Maintenance comparison

Focus on plants that maintain the same design role and visual impact."""

    @staticmethod
    def validate_list_prompt(plants: List[str], zone: int, sun: str, water: str) -> str:
        """
        Generate prompt for validating a plant list.

        Returns:
            Formatted prompt string
        """
        plant_list = "\n".join(f"- {p}" for p in plants)

        return f"""Validate this plant list for residential installation.

Plants:
{plant_list}

Site conditions:
- Zone: {zone}
- Sun: {sun}
- Water: {water}

Check and report on:
1. Zone compatibility - will each plant survive?
2. Sun/water match - are conditions appropriate?
3. Mature size conflicts - will plants outgrow the space?
4. Role coverage - are all design roles filled?
5. Maintenance level - is the overall plan realistic?
6. Design cohesion - do the plants work together?

Flag anything uncertain for user verification.
Suggest replacements for any plants that don't work."""

    @staticmethod
    def seasonal_interest_prompt(style: str, zone: int) -> str:
        """
        Generate prompt for creating seasonal interest plan.

        Returns:
            Formatted prompt string
        """
        return f"""Create a four-season interest planting plan.

Style: {style}
Zone: {zone}

For each season, recommend:

SPRING:
- 2-3 plants for spring bloom or emerging foliage
- Focus on early color after winter

SUMMER:
- 2-3 plants for summer bloom or texture
- Consider heat tolerance

FALL:
- 2-3 plants for fall color or late bloom
- Include ornamental grasses if appropriate

WINTER:
- 2-3 plants for winter structure
- Evergreens, bark interest, or persistent seed heads

Return a cohesive palette where plants complement each other
across all seasons."""


class PlantPaletteBuilder:
    """
    Build curated plant palettes for different purposes.
    """

    @staticmethod
    def build_pollinator_palette(zone: int, sun: str) -> Dict[str, List[str]]:
        """Build a pollinator-friendly palette"""
        return {
            "spring_nectar": [
                "Cercis canadensis (Eastern Redbud)",
                "Phlox subulata (Creeping Phlox)",
                "Salvia nemorosa (Woodland Sage)"
            ],
            "summer_nectar": [
                "Caryopteris x clandonensis (Blue Mist Shrub)",
                "Perovskia atriplicifolia (Russian Sage)",
                "Lavandula angustifolia (English Lavender)"
            ],
            "fall_nectar": [
                "Sedum spurium (Two Row Stonecrop)",
                "Aster species (Native Asters)",
                "Solidago species (Goldenrod)"
            ],
            "host_plants": [
                "Asclepias species (Milkweed)",
                "Carex species (Native Sedges)",
                "Quercus species (Native Oaks)"
            ],
            "notes": [
                "Include plants with different bloom times",
                "Provide sheltered areas for nesting",
                "Avoid pesticides in the landscape"
            ]
        }

    @staticmethod
    def build_low_water_palette(zone: int) -> Dict[str, List[str]]:
        """Build a drought-tolerant palette"""
        return {
            "structural": [
                "Juniperus chinensis 'Sea Green'",
                "Taxus x media 'Densiformis'"
            ],
            "accent": [
                "Perovskia atriplicifolia (Russian Sage)",
                "Lavandula angustifolia (English Lavender)",
                "Caryopteris x clandonensis (Blue Mist Shrub)"
            ],
            "groundcover": [
                "Sedum spurium (Two Row Stonecrop)",
                "Dianthus gratianopolitanus (Cheddar Pinks)",
                "Phlox subulata (Creeping Phlox)"
            ],
            "design_tips": [
                "Group plants by water needs",
                "Use mulch to retain moisture",
                "Install drip irrigation for establishment",
                "Accept natural dormancy in heat"
            ]
        }

    @staticmethod
    def build_shade_palette(zone: int, water: str) -> Dict[str, List[str]]:
        """Build a shade-tolerant palette"""
        return {
            "structural": [
                "Rhododendron catawbiense (Catawba Rhododendron)",
                "Ilex crenata 'Compacta' (Compact Japanese Holly)",
                "Taxus x media 'Densiformis' (Dense Spreading Yew)"
            ],
            "accent": [
                "Hydrangea macrophylla (Bigleaf Hydrangea)",
                "Heuchera villosa (Hairy Alumroot)"
            ],
            "groundcover": [
                "Pachysandra terminalis (Japanese Spurge)",
                "Vinca minor (Periwinkle)",
                "Ajuga reptans (Bugleweed)"
            ],
            "understory": [
                "Cornus florida (Flowering Dogwood)",
                "Acer palmatum (Japanese Maple)",
                "Chionanthus virginicus (White Fringetree)"
            ],
            "design_tips": [
                "Focus on foliage texture and color",
                "Use variegated plants to brighten",
                "Layer heights for depth",
                "Accept that bloom will be limited"
            ]
        }

    @staticmethod
    def build_four_season_palette(zone: int, style: str) -> Dict[str, Any]:
        """Build a four-season interest palette"""
        return {
            "spring": {
                "focus": "Bloom and emerging foliage",
                "plants": [
                    "Cercis canadensis (Redbud) - pink flowers",
                    "Spiraea japonica 'Goldflame' - golden new growth",
                    "Phlox subulata - flower carpet"
                ]
            },
            "summer": {
                "focus": "Flowers and lush foliage",
                "plants": [
                    "Hydrangea paniculata 'Limelight' - large panicles",
                    "Rosa 'Knock Out' - continuous bloom",
                    "Perovskia atriplicifolia - blue spikes"
                ]
            },
            "fall": {
                "focus": "Foliage color and late bloom",
                "plants": [
                    "Acer rubrum - brilliant red",
                    "Viburnum dentatum - purple foliage, blue berries",
                    "Nandina domestica - red-bronze foliage"
                ]
            },
            "winter": {
                "focus": "Structure and evergreen presence",
                "plants": [
                    "Thuja occidentalis 'Emerald' - bright green",
                    "Ilex opaca - berries and dark green",
                    "Juniperus virginiana - blue-green texture"
                ]
            },
            "year_round_backbone": [
                "Buxus sempervirens (Boxwood)",
                "Prunus laurocerasus 'Otto Luyken'",
                "Taxus x media"
            ]
        }


def main():
    """Demo the design advisor functionality"""
    print("=" * 60)
    print("Design Advisor - Demo")
    print("=" * 60)

    # Get design brief
    print("\n--- Design Brief: Craftsman Front Yard ---")
    brief = ResidentialDesignAdvisor.generate_design_brief(
        style="craftsman",
        space="front_yard",
        zone=7,
        sun="full",
        water="average"
    )
    print(f"Style: {brief['project']['style']}")
    print(f"Principles: {', '.join(brief['design_direction']['principles'])}")
    print(f"Tips: {brief['design_tips'][0]}")

    # Compare styles
    print("\n--- Style Comparison ---")
    comparison = ResidentialDesignAdvisor.get_style_comparison()
    for style, data in list(comparison.items())[:3]:
        print(f"  {data['name']}: {data['spacing']}")

    # Generate AI prompt
    print("\n--- AI Prompt Generation ---")
    prompt = AIPromptGenerator.build_package_prompt(
        style="modern",
        space="front_yard",
        zone=6,
        sun="full",
        water="average"
    )
    print(f"Prompt preview: {prompt[:200]}...")

    # Build palette
    print("\n--- Four Season Palette ---")
    palette = PlantPaletteBuilder.build_four_season_palette(7, "craftsman")
    print(f"Spring: {palette['spring']['plants'][0]}")
    print(f"Summer: {palette['summer']['plants'][0]}")
    print(f"Fall: {palette['fall']['plants'][0]}")
    print(f"Winter: {palette['winter']['plants'][0]}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

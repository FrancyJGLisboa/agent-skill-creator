#!/usr/bin/env python3
"""
Design Advisor for Home Plant Trainer

Provides:
- Style-based design packages (Traditional, Farmhouse, Craftsman, Modern)
- Client-facing explanation engine for proposals
- Location-based design models (Front Yard, Backyard, Side Yard)
- Design philosophy from respected sources

Based on design principles from:
- Better Homes & Gardens
- Sunset Magazine
- Architectural Digest
- Houzz
- Landscaping Network
- Yardzen
- Frederick Law Olmsted design philosophy
- The Cultural Landscape Foundation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


# ============================================================================
# STYLE PACKAGES
# ============================================================================

@dataclass
class StylePackage:
    """Complete design style package with principles and preferences."""

    name: str
    description: str
    principles: List[str]
    form_preferences: List[str]
    color_palette: List[str]
    spacing_approach: str
    texture_preferences: List[str]
    seasonal_emphasis: str
    example_plants: List[str]
    avoid_plants: List[str]
    architectural_harmony: str


# Style package definitions
STYLE_PACKAGES: Dict[str, StylePackage] = {
    "traditional": StylePackage(
        name="Traditional / Colonial",
        description="Formal, balanced aesthetic with symmetry and classic structure. "
                    "Emphasizes clean lines, foundation hedges, and seasonal color near entry points.",
        principles=[
            "Symmetry in plant placement",
            "Foundation hedges for definition",
            "Evergreen backbone for year-round structure",
            "Seasonal color concentrated near entries",
            "Clean, manicured appearance",
            "Balance between sides of home/walkway"
        ],
        form_preferences=["rounded", "columnar", "pyramidal", "formal"],
        color_palette=["green", "white", "pink", "red accents"],
        spacing_approach="Regular, formal spacing with geometric patterns. "
                        "Equal distances between plants of the same type.",
        texture_preferences=["fine to medium", "uniform", "clipped"],
        seasonal_emphasis="Year-round structure with spring/summer color accents",
        example_plants=[
            "Boxwood", "Yew", "Azalea", "Hydrangea",
            "Japanese Holly", "American Holly", "Knockout Rose"
        ],
        avoid_plants=["Wild grasses", "Naturalistic perennials", "Asymmetric forms"],
        architectural_harmony="Reinforces formal architecture. Plants mirror the "
                             "symmetry and order of the home facade."
    ),

    "farmhouse": StylePackage(
        name="Farmhouse",
        description="Informal, naturalistic character with native and naturalized species. "
                    "Emphasizes texture, open lawn sightlines, and relaxed groupings.",
        principles=[
            "Open lawn sightlines preserved",
            "Native or naturalized plant selections",
            "Informal, asymmetric grouping",
            "Emphasis on texture over formal shape",
            "Functional planting (herbs, cutting flowers)",
            "Loose, relaxed borders"
        ],
        form_preferences=["mounding", "fountain", "spreading", "natural"],
        color_palette=["soft pastels", "whites", "lavenders", "yellows", "greens"],
        spacing_approach="Irregular, naturalistic spacing. Plants grouped in odd numbers "
                        "with varied distances creating depth.",
        texture_preferences=["mixed textures", "grasses", "soft", "flowing"],
        seasonal_emphasis="Summer abundance with fall harvest themes",
        example_plants=[
            "Hydrangea", "Lavender", "Black-Eyed Susan", "Coneflower",
            "Switchgrass", "Viburnum", "Serviceberry"
        ],
        avoid_plants=["Heavily sheared hedges", "Formal topiaries", "Exotic tropicals"],
        architectural_harmony="Complements rustic, relaxed architecture. Creates "
                             "a welcoming, lived-in feeling around the home."
    ),

    "craftsman": StylePackage(
        name="Craftsman",
        description="Layered, natural material harmony with strong horizontal lines. "
                    "Emphasizes entry-focused design and integration with home architecture.",
        principles=[
            "Strong horizontal lines echoing home design",
            "Natural stone and native materials",
            "Layered evergreen backbones",
            "Entry emphasis with grouped plantings",
            "Integration with architectural elements",
            "Natural color palette"
        ],
        form_preferences=["layered", "horizontal", "mounding", "upright"],
        color_palette=["earth tones", "greens", "burgundy", "rust", "gold"],
        spacing_approach="Grouped plantings with clear layering from low to high. "
                        "Plants arranged to emphasize horizontal sight lines.",
        texture_preferences=["medium to coarse", "varied", "natural"],
        seasonal_emphasis="Four-season interest with emphasis on structure",
        example_plants=[
            "Japanese Maple", "Yew", "Oregon Grape", "Oakleaf Hydrangea",
            "Nandina", "Kousa Dogwood", "Witch Hazel"
        ],
        avoid_plants=["Tropical plants", "Highly formal shapes", "Garish colors"],
        architectural_harmony="Echoes the handcrafted, natural aesthetic of Craftsman homes. "
                             "Plants reinforce horizontal lines and earthy materials."
    ),

    "modern": StylePackage(
        name="Modern / Contemporary",
        description="Minimalist, architectural clarity with repetition over variety. "
                    "Emphasizes strong negative space and sculptural plant forms.",
        principles=[
            "Minimal plant palette (few species)",
            "Repetition for visual impact",
            "Strong negative space",
            "Architectural plant forms",
            "Clean, uncluttered design",
            "Geometric arrangements"
        ],
        form_preferences=["columnar", "spherical", "linear", "architectural"],
        color_palette=["green", "silver", "white", "burgundy", "black"],
        spacing_approach="Precise, intentional spacing with generous gaps. "
                        "Repetition of single species in mass plantings.",
        texture_preferences=["bold", "singular", "dramatic contrast"],
        seasonal_emphasis="Year-round structure over seasonal variation",
        example_plants=[
            "Boxwood", "Maiden Grass", "Loropetalum", "Pittosporum",
            "Clumping Bamboo", "Creeping Juniper", "Japanese Maple"
        ],
        avoid_plants=["Cottage-style perennials", "Mixed color beds", "Fussy plants"],
        architectural_harmony="Complements clean lines of modern architecture. "
                             "Plants become sculptural elements, not decoration."
    ),

    "cottage": StylePackage(
        name="Cottage",
        description="Abundant, romantic abundance with informal borders and mixed plantings. "
                    "Emphasizes color, fragrance, and a sense of overflowing beauty.",
        principles=[
            "Abundant, full plantings",
            "Mixed borders with perennials and shrubs",
            "Fragrance prioritized",
            "Self-seeding and spreading welcome",
            "Romantic, slightly wild appearance",
            "Color throughout the seasons"
        ],
        form_preferences=["mounding", "spreading", "billowing", "arching"],
        color_palette=["pinks", "purples", "blues", "whites", "soft yellows"],
        spacing_approach="Close spacing for lush appearance. Plants allowed to "
                        "intermingle and soften edges.",
        texture_preferences=["fine to medium", "soft", "flowing", "varied"],
        seasonal_emphasis="Peak summer bloom with continuous color",
        example_plants=[
            "Hydrangea", "Lavender", "Roses", "Hosta", "Azalea",
            "Daylily", "Butterfly Bush", "Fern"
        ],
        avoid_plants=["Rigid architectural forms", "Sparse plantings", "Minimalist layouts"],
        architectural_harmony="Softens architecture with abundant plantings. "
                             "Creates a sense of age and romantic charm."
    ),

    "naturalistic": StylePackage(
        name="Naturalistic / Native",
        description="Ecological, native planting that prioritizes regional species, "
                    "wildlife habitat, and low-input sustainability.",
        principles=[
            "Native species priority",
            "Ecological function (habitat, pollinators)",
            "Low-input, sustainable design",
            "Meadow-like drifts",
            "Seasonal dynamics embraced",
            "Natural plant communities replicated"
        ],
        form_preferences=["natural", "fountain", "spreading", "upright"],
        color_palette=["native flower colors", "greens", "golds", "purple"],
        spacing_approach="Drifts and masses mimicking natural plant communities. "
                        "Irregular spacing reflecting wild patterns.",
        texture_preferences=["varied", "grasses dominant", "natural"],
        seasonal_emphasis="Four-season dynamics with peak summer/fall interest",
        example_plants=[
            "Coneflower", "Black-Eyed Susan", "Switchgrass", "Viburnum",
            "Inkberry Holly", "Eastern Red Cedar", "Redbud"
        ],
        avoid_plants=["Exotic species", "High-maintenance plants", "Non-native cultivars"],
        architectural_harmony="Integrates home into the natural landscape. "
                             "Blurs boundaries between garden and wild."
    ),
}


# ============================================================================
# LOCATION-BASED DESIGN MODELS
# ============================================================================

@dataclass
class LocationModel:
    """Design model for a specific yard location."""

    name: str
    primary_function: str
    key_principles: List[str]
    essential_roles: List[str]
    design_priorities: List[str]
    common_challenges: List[str]
    source_references: List[str]


LOCATION_MODELS: Dict[str, LocationModel] = {
    "front_yard": LocationModel(
        name="Front Yard / Curb Appeal",
        primary_function="Creates first impression, frames architecture, welcomes visitors",
        key_principles=[
            "Entry framing - guide the eye to the front door",
            "Foundation integration - soften home base without blocking windows",
            "Curb extension - connect home to street/neighborhood",
            "Layered depth - create interest without cluttering",
            "Year-round structure - maintain appeal in all seasons"
        ],
        essential_roles=["structural", "foundation", "accent", "edge"],
        design_priorities=[
            "Architectural harmony with home style",
            "Clear sight lines to entry",
            "Low-maintenance curb presence",
            "Seasonal color near high-visibility areas"
        ],
        common_challenges=[
            "Foundation height constraints (windows, vents)",
            "Utility easements and setbacks",
            "Full sun exposure typical",
            "High visibility = higher maintenance expectations"
        ],
        source_references=[
            "Better Homes & Gardens - Front Yard & Curb Appeal",
            "Yardzen - Style-Based Front Yard Design"
        ]
    ),

    "backyard": LocationModel(
        name="Backyard / Outdoor Living",
        primary_function="Extends living space, provides privacy, creates outdoor rooms",
        key_principles=[
            "Outdoor room creation - defined spaces for activities",
            "Privacy screening - buffer from neighbors",
            "Shade provision - canopy for comfort",
            "Layered enclosure - plants as walls and ceiling",
            "Four-season usability - structure that works year-round"
        ],
        essential_roles=["canopy", "screening", "structural", "accent", "groundcover"],
        design_priorities=[
            "Privacy from adjacent properties",
            "Shade for outdoor activities",
            "Integration with hardscape areas",
            "Wildlife habitat opportunity"
        ],
        common_challenges=[
            "Varying sun/shade across space",
            "Privacy needs at multiple heights",
            "Integration with patio/deck areas",
            "Balance of open and planted space"
        ],
        source_references=[
            "Better Homes & Gardens - Backyard Outdoor Living",
            "Architectural Digest - Garden Design Principles"
        ]
    ),

    "side_yard": LocationModel(
        name="Side Yard / Transition Zone",
        primary_function="Provides utility, screening, and design continuity between front and back",
        key_principles=[
            "Continuity - connect front and back design language",
            "Screening - control views to/from neighbors",
            "Efficiency - maximize narrow spaces",
            "Utility - accommodate AC units, trash, storage",
            "Low maintenance - often overlooked, needs durability"
        ],
        essential_roles=["screening", "structural", "groundcover"],
        design_priorities=[
            "Visual screening from neighbors",
            "Design continuity with front/back",
            "Low-maintenance plant choices",
            "Functional access maintained"
        ],
        common_challenges=[
            "Narrow width constraints",
            "Heavy shade from home/neighbors",
            "Poor soil from construction",
            "Utility interference (AC, meters)"
        ],
        source_references=[
            "Sunset Magazine - Side Yard Solutions",
            "Landscaping Network - Narrow Space Design"
        ]
    ),
}


# ============================================================================
# DESIGN ADVISOR
# ============================================================================

class DesignAdvisor:
    """
    Provides design guidance, style packages, and proposal explanations.

    Sources integrated:
    - Better Homes & Gardens: Home-integrated landscape principles
    - Sunset Magazine: Regional/climate-aware design
    - Architectural Digest: High-end design perspectives
    - Houzz: Real project examples
    - Yardzen: Style classification system
    - Frederick Law Olmsted: Foundational design philosophy
    - The Cultural Landscape Foundation: Professional practice context
    """

    def __init__(self):
        self.styles = STYLE_PACKAGES
        self.locations = LOCATION_MODELS

    def get_style_package(self, style) -> StylePackage:
        """Get the design package for a specific style."""
        style_key = style.value if hasattr(style, 'value') else style
        return self.styles.get(style_key, self.styles["traditional"])

    def get_location_model(self, location) -> LocationModel:
        """Get the design model for a specific location."""
        location_key = location.value if hasattr(location, 'value') else location
        return self.locations.get(location_key, self.locations["front_yard"])

    def generate_proposal_explanation(
        self,
        request,
        design: Dict[str, Any]
    ) -> str:
        """
        Generate client-facing explanation for a design proposal.

        Uses template-based language for consistency and professionalism.
        """
        style_package = self.get_style_package(request.style)
        location_model = self.get_location_model(request.location)
        conditions = request.site_conditions

        # Build the explanation
        sections = []

        # Design Intent Section
        sections.append(self._generate_design_intent_section(
            style_package, location_model
        ))

        # Site Constraints Section
        sections.append(self._generate_site_constraints_section(conditions))

        # Plant Selection Rationale Section
        sections.append(self._generate_selection_rationale_section(
            design, style_package
        ))

        # Maintenance Guidance Section
        sections.append(self._generate_maintenance_section(
            conditions.maintenance_level, design
        ))

        # Seasonal Interest Section
        sections.append(self._generate_seasonal_section(design))

        return "\n\n".join(sections)

    def _generate_design_intent_section(
        self,
        style: StylePackage,
        location: LocationModel
    ) -> str:
        """Generate the design intent explanation."""
        return (
            f"## Design Intent\n\n"
            f"This planting plan is designed to create a cohesive, home-integrated "
            f"landscape with year-round structure and seasonal interest.\n\n"
            f"**Style Approach: {style.name}**\n"
            f"{style.description}\n\n"
            f"**Location Focus: {location.name}**\n"
            f"{location.primary_function}\n\n"
            f"**Key Design Principles:**\n"
            + "\n".join([f"- {p}" for p in style.principles[:4]])
        )

    def _generate_site_constraints_section(self, conditions) -> str:
        """Generate site constraints acknowledgment."""
        zone = conditions.usda_zone
        sun = conditions.sun_exposure.value if hasattr(conditions.sun_exposure, 'value') else conditions.sun_exposure
        water = conditions.water_profile.value if hasattr(conditions.water_profile, 'value') else conditions.water_profile
        maintenance = conditions.maintenance_level.value if hasattr(conditions.maintenance_level, 'value') else conditions.maintenance_level

        text = (
            f"## Site Conditions\n\n"
            f"Plant selections are matched to your property's specific conditions:\n\n"
            f"- **USDA Hardiness Zone:** {zone}\n"
            f"- **Sun Exposure:** {sun.title()}\n"
            f"- **Moisture Profile:** {water.title()}\n"
            f"- **Target Maintenance Level:** {maintenance.title()}"
        )

        if conditions.height_limit_ft:
            text += f"\n- **Height Constraint:** Maximum {conditions.height_limit_ft} ft"

        if conditions.width_limit_ft:
            text += f"\n- **Width Constraint:** Maximum {conditions.width_limit_ft} ft"

        if conditions.deer_pressure:
            text += "\n- **Special Consideration:** Deer-resistant selections prioritized"

        if conditions.salt_exposure:
            text += "\n- **Special Consideration:** Salt-tolerant species selected"

        return text

    def _generate_selection_rationale_section(
        self,
        design: Dict[str, Any],
        style: StylePackage
    ) -> str:
        """Generate plant selection rationale."""
        selections = design.get("plant_selections", {})

        text = (
            f"## Plant Selection Rationale\n\n"
            f"Each plant was selected to fulfill a specific role in the design "
            f"while meeting your site conditions and {style.name.lower()} aesthetic.\n"
        )

        for role, plants in selections.items():
            if plants:
                text += f"\n### {role.replace('_', ' ').title()} Layer\n"
                for plant in plants[:2]:  # Top 2 for each role
                    text += (
                        f"\n**{plant['plant_name']}** ({plant['botanical_name']})\n"
                        f"- Form: {plant['form'].title()}\n"
                        f"- Mature Size: {plant['mature_size']}\n"
                        f"- Selection Factors: {plant['selection_reasoning']}\n"
                    )

        return text

    def _generate_maintenance_section(
        self,
        maintenance_level,
        design: Dict[str, Any]
    ) -> str:
        """Generate maintenance guidance."""
        level = maintenance_level.value if hasattr(maintenance_level, 'value') else maintenance_level

        level_descriptions = {
            "low": "minimal intervention with plants selected for durability and self-sufficiency",
            "medium": "regular seasonal care with moderate pruning and attention",
            "high": "active maintenance with frequent pruning, deadheading, and attention"
        }

        return (
            f"## Maintenance Guidance\n\n"
            f"This plan is designed for **{level} maintenance** - "
            f"{level_descriptions.get(level, level_descriptions['medium'])}.\n\n"
            f"{design.get('maintenance_summary', 'All selections align with maintenance goals.')}"
        )

    def _generate_seasonal_section(self, design: Dict[str, Any]) -> str:
        """Generate seasonal interest timeline."""
        timeline = design.get("seasonal_timeline", {})

        text = "## Seasonal Interest Timeline\n"

        season_emojis = {
            "spring": "Spring",
            "summer": "Summer",
            "fall": "Fall",
            "winter": "Winter"
        }

        for season, interests in timeline.items():
            if interests:
                text += f"\n**{season_emojis.get(season, season.title())}:**\n"
                for interest in interests[:3]:  # Top 3 per season
                    text += f"- {interest}\n"

        return text

    def generate_swap_justification(
        self,
        original_plant: str,
        replacement_plant: str,
        role: str,
        reason: str
    ) -> str:
        """
        Generate justification for a plant swap recommendation.

        Template for consistent client communication.
        """
        return (
            f"We recommend **{replacement_plant}** instead of **{original_plant}** "
            f"to maintain the same design role ({role}) while improving performance "
            f"under your site conditions. {reason}"
        )

    def get_design_philosophy(self) -> Dict[str, str]:
        """
        Return core design philosophy principles from respected sources.
        """
        return {
            "olmsted_principle": (
                "Design working organically with the landscape, emphasizing "
                "utility and natural features over artificial imposition."
            ),
            "bhg_principle": (
                "Integration with architecture - making landscape feel like "
                "a natural extension of the home facade."
            ),
            "sunset_principle": (
                "Climate-aware design that respects regional growing conditions "
                "and reduces maintenance through appropriate plant selection."
            ),
            "yardzen_principle": (
                "Style-based design vocabulary that creates cohesion through "
                "consistent form, spacing, and material choices."
            ),
            "universal_rule": (
                "Design principles never change - plants adapt. Form, scale, "
                "and role remain constant while species respond to conditions."
            )
        }

    def get_role_design_guidance(self, role: str) -> Dict[str, Any]:
        """
        Get design guidance for a specific plant role.
        """
        role_guidance = {
            "structural": {
                "function": "Holds the design together year-round",
                "placement": "Primary visual anchors, corners, and repeated rhythm points",
                "selection_priority": "Form and year-round presence over flower",
                "typical_count": "3-7 per 1000 sq ft depending on space"
            },
            "accent": {
                "function": "Provides focal points and seasonal moments",
                "placement": "Near entries, at sight-line terminations, feature areas",
                "selection_priority": "Bloom impact, unique form, or striking texture",
                "typical_count": "1-3 per focal area"
            },
            "screening": {
                "function": "Creates privacy and visual buffers",
                "placement": "Property lines, utility concealment, neighbor buffering",
                "selection_priority": "Density, height, reliability, fast establishment",
                "typical_count": "Continuous mass or staggered rows"
            },
            "foundation": {
                "function": "Softens home base and transitions architecture to landscape",
                "placement": "Along foundation walls, under windows, beside entries",
                "selection_priority": "Mature height below windows, clean habit",
                "typical_count": "Continuous or rhythmic along foundation"
            },
            "groundcover": {
                "function": "Unifies planting areas and suppresses weeds",
                "placement": "Under trees, between shrubs, bed edges",
                "selection_priority": "Spreading habit, low height, durability",
                "typical_count": "Mass planting for visual impact"
            },
            "canopy": {
                "function": "Provides overhead structure and shade",
                "placement": "Strategic positions considering mature size and shade patterns",
                "selection_priority": "Appropriate scale, root behavior, longevity",
                "typical_count": "1-3 per typical residential lot"
            },
            "understory": {
                "function": "Creates mid-layer depth and seasonal interest",
                "placement": "Under canopy trees, as specimens, at layer transitions",
                "selection_priority": "Four-season interest, shade tolerance if needed",
                "typical_count": "1-5 depending on canopy presence"
            }
        }

        return role_guidance.get(role, role_guidance["structural"])


# ============================================================================
# CLIMATE SWAP LOGIC
# ============================================================================

class ClimateSwapAdvisor:
    """
    Provides climate-based plant swap recommendations.

    Core Rule: Design principles never change - plants adapt.
    """

    @staticmethod
    def get_swap_rules() -> Dict[str, str]:
        """Get the core swap rules for climate adaptation."""
        return {
            "zone_rule": (
                "When moving to a colder zone, replace with cold-hardy species "
                "that maintain the same form and scale."
            ),
            "heat_rule": (
                "When moving to a warmer zone, select heat-tolerant species "
                "with matching growth habit and size."
            ),
            "water_rule": (
                "Water tolerance overrides zone if drainage is poor. "
                "Wet sites require moisture-tolerant selections regardless of zone."
            ),
            "sun_rule": (
                "Shade designs rely on leaf quality, not flowers. "
                "Part shade allows most flexibility in selection."
            ),
            "size_rule": (
                "Mature size constraints are non-negotiable. "
                "Never recommend plants that exceed spatial limits."
            ),
            "role_rule": (
                "Never swap across roles unless no options exist. "
                "Role integrity maintains design intent."
            )
        }

    @staticmethod
    def get_equivalent_forms() -> Dict[str, List[str]]:
        """Get form equivalency for swap recommendations."""
        return {
            "rounded": ["mounding", "globular"],
            "upright": ["columnar", "vase"],
            "spreading": ["horizontal", "prostrate"],
            "pyramidal": ["conical"],
            "layered": ["horizontal branching"],
            "fountain": ["arching", "weeping"]
        }

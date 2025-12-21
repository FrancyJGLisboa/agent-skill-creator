"""
Home Plant Trainer - Main Orchestrator

Adaptive residential plant design advisor for home landscapes.
Zone-aware, condition-driven plant selection with automatic species
swapping based on USDA zone, sun exposure, water needs, and size constraints.

Plant-only designs - no hardscape recommendations.

Example Usage:
    trainer = HomePlantTrainer()
    result = trainer.design_planting(
        zone=7,
        sun="full",
        water="average",
        space="front_yard",
        style="craftsman"
    )
"""

from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class PlantRole(Enum):
    """Plant roles in residential landscape design"""
    STRUCTURAL = "structural"
    ACCENT = "accent"
    SCREENING = "screening"
    FOUNDATION_SOFTENER = "foundation_softener"
    EDGE_BORDER = "edge_border"
    GROUNDCOVER = "groundcover"
    CANOPY = "canopy"
    UNDERSTORY = "understory"


class PlantLayer(Enum):
    """Vertical layers in planting design"""
    CANOPY = "canopy"
    UNDERSTORY = "understory"
    SHRUB = "shrub"
    HERBACEOUS = "herbaceous"
    GROUNDCOVER = "groundcover"


class PlantForm(Enum):
    """Plant growth forms"""
    COLUMNAR = "columnar"
    ROUNDED = "rounded"
    MOUNDING = "mounding"
    SPREADING = "spreading"
    VASE = "vase"
    WEEPING = "weeping"
    UPRIGHT = "upright"
    PYRAMIDAL = "pyramidal"


class DesignStyle(Enum):
    """Residential landscape design styles"""
    TRADITIONAL = "traditional"
    COLONIAL = "colonial"
    FARMHOUSE = "farmhouse"
    CRAFTSMAN = "craftsman"
    MODERN = "modern"
    COTTAGE = "cottage"
    NATURALISTIC = "naturalistic"


class YardSpace(Enum):
    """Yard location types"""
    FRONT_YARD = "front_yard"
    BACKYARD = "backyard"
    SIDE_YARD = "side_yard"


@dataclass
class SiteConditions:
    """Site-specific growing conditions"""
    usda_zone: int
    zone_suffix: str = ""  # "a" or "b"
    sun_exposure: str = "full"  # full, part, shade
    water_profile: str = "average"  # dry, average, wet
    soil_type: str = "loam"  # clay, loam, sand
    space_height_limit: float = 20.0  # feet
    space_width_limit: float = 10.0  # feet
    maintenance_tolerance: str = "medium"  # low, medium, high
    wind_exposure: str = "sheltered"  # sheltered, open
    deer_pressure: bool = False
    salt_exposure: bool = False


@dataclass
class PlantRecommendation:
    """A single plant recommendation with full details"""
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


class PlantRoleMatrix:
    """
    Defines plant roles and their characteristics for residential design.

    Training Rule: Every theme package fills the same roles with different species.
    """

    ROLE_DEFINITIONS = {
        PlantRole.STRUCTURAL: {
            "description": "Holds design together year-round (backbone)",
            "layer": PlantLayer.SHRUB,
            "typical_form": [PlantForm.ROUNDED, PlantForm.UPRIGHT],
            "height_range": (3, 8),
            "must_tolerate_pruning": True,
            "dense_habit": True
        },
        PlantRole.ACCENT: {
            "description": "Focal points, seasonal punch, visual moments",
            "layer": PlantLayer.SHRUB,
            "typical_form": [PlantForm.MOUNDING, PlantForm.UPRIGHT],
            "height_range": (1, 6),
            "bloom_texture_priority": True
        },
        PlantRole.SCREENING: {
            "description": "Privacy, view control, buffering",
            "layer": PlantLayer.SHRUB,
            "typical_form": [PlantForm.UPRIGHT, PlantForm.COLUMNAR],
            "height_range": (6, 25),
            "must_be_dense": True,
            "reliable": True
        },
        PlantRole.FOUNDATION_SOFTENER: {
            "description": "Reduces harsh lines of home base",
            "layer": PlantLayer.SHRUB,
            "typical_form": [PlantForm.ROUNDED],
            "height_range": (2, 5),
            "must_not_block_windows": True
        },
        PlantRole.EDGE_BORDER: {
            "description": "Clean bed lines, lawn transitions, pathway edges",
            "layer": PlantLayer.GROUNDCOVER,
            "typical_form": [PlantForm.MOUNDING],
            "height_range": (0.5, 1.5),
            "must_stay_tidy": True
        },
        PlantRole.GROUNDCOVER: {
            "description": "Covers soil, suppresses weeds, unifies layers",
            "layer": PlantLayer.GROUNDCOVER,
            "typical_form": [PlantForm.SPREADING, PlantForm.MOUNDING],
            "height_range": (0.17, 1),  # 2-12 inches
            "erosion_control": True
        },
        PlantRole.CANOPY: {
            "description": "Overhead structure, microclimate builder",
            "layer": PlantLayer.CANOPY,
            "typical_form": [PlantForm.ROUNDED, PlantForm.COLUMNAR, PlantForm.VASE],
            "height_range": (20, 60),
            "must_fit_setbacks": True
        },
        PlantRole.UNDERSTORY: {
            "description": "Mid-layer depth, seasonal interest, scale control",
            "layer": PlantLayer.UNDERSTORY,
            "typical_form": [PlantForm.ROUNDED, PlantForm.VASE],
            "height_range": (10, 25),
            "shade_tolerant": True
        }
    }

    @classmethod
    def get_role_requirements(cls, role: PlantRole) -> Dict:
        """Get the requirements for a specific plant role"""
        return cls.ROLE_DEFINITIONS.get(role, {})

    @classmethod
    def get_fallback_roles(cls, role: PlantRole) -> List[PlantRole]:
        """Get permitted fallback roles if no plants match primary role"""
        fallbacks = {
            PlantRole.STRUCTURAL: [PlantRole.FOUNDATION_SOFTENER, PlantRole.SCREENING],
            PlantRole.ACCENT: [PlantRole.STRUCTURAL],
            PlantRole.GROUNDCOVER: [PlantRole.EDGE_BORDER],
            PlantRole.SCREENING: [PlantRole.STRUCTURAL],
            PlantRole.UNDERSTORY: [PlantRole.SCREENING, PlantRole.STRUCTURAL]
        }
        return fallbacks.get(role, [])


class StylePackages:
    """
    Style-based planting packages for different residential aesthetics.

    Each style defines plant characteristics, NOT specific species.
    Species are selected based on site conditions.
    """

    STYLES = {
        DesignStyle.TRADITIONAL: {
            "name": "Traditional / Colonial",
            "principles": ["symmetry", "formal_structure", "classic_palette"],
            "plant_characteristics": {
                "structural": {
                    "form_preference": [PlantForm.ROUNDED, PlantForm.PYRAMIDAL],
                    "prefer_evergreen": True,
                    "hedge_suitable": True
                },
                "accent": {
                    "seasonal_color_near_entry": True,
                    "classic_bloom_colors": ["white", "pink", "red"]
                },
                "foundation": {
                    "formal_hedges": True,
                    "uniform_spacing": True
                }
            },
            "spacing_style": "formal",
            "color_palette": ["deep_green", "white", "pink", "classic_red"]
        },

        DesignStyle.FARMHOUSE: {
            "name": "Farmhouse",
            "principles": ["open_sightlines", "informal_grouping", "naturalized"],
            "plant_characteristics": {
                "structural": {
                    "form_preference": [PlantForm.ROUNDED, PlantForm.MOUNDING],
                    "native_preferred": True,
                    "texture_emphasis": True
                },
                "accent": {
                    "cottage_style_blooms": True,
                    "informal_masses": True
                },
                "groundcover": {
                    "naturalized_drifts": True
                }
            },
            "spacing_style": "informal",
            "color_palette": ["soft_green", "white", "lavender", "soft_pink", "yellow"]
        },

        DesignStyle.CRAFTSMAN: {
            "name": "Craftsman",
            "principles": ["horizontal_lines", "natural_materials_echo", "layered_evergreens"],
            "plant_characteristics": {
                "structural": {
                    "form_preference": [PlantForm.MOUNDING, PlantForm.SPREADING],
                    "layered_arrangement": True,
                    "evergreen_backbone": True
                },
                "accent": {
                    "entry_emphasis": True,
                    "natural_color_palette": True
                },
                "foundation": {
                    "strong_horizontal_lines": True,
                    "medium_scale": True
                }
            },
            "spacing_style": "layered",
            "color_palette": ["forest_green", "bronze", "rust", "cream", "gold"]
        },

        DesignStyle.MODERN: {
            "name": "Modern / Contemporary",
            "principles": ["minimal_palette", "repetition", "architectural_forms"],
            "plant_characteristics": {
                "structural": {
                    "form_preference": [PlantForm.COLUMNAR, PlantForm.UPRIGHT],
                    "architectural_plants": True,
                    "limited_species_count": True
                },
                "accent": {
                    "bold_foliage": True,
                    "sculptural_forms": True
                },
                "groundcover": {
                    "uniform_mass": True,
                    "clean_lines": True
                }
            },
            "spacing_style": "geometric",
            "color_palette": ["dark_green", "silver", "burgundy", "white", "black"]
        },

        DesignStyle.COTTAGE: {
            "name": "Cottage Garden",
            "principles": ["abundance", "mixed_borders", "romantic_style"],
            "plant_characteristics": {
                "structural": {
                    "form_preference": [PlantForm.ROUNDED, PlantForm.MOUNDING],
                    "backdrop_for_perennials": True
                },
                "accent": {
                    "abundant_blooms": True,
                    "layered_heights": True,
                    "continuous_bloom": True
                },
                "edge": {
                    "spilling_over_edges": True
                }
            },
            "spacing_style": "dense_mixed",
            "color_palette": ["pink", "purple", "blue", "white", "soft_yellow"]
        },

        DesignStyle.NATURALISTIC: {
            "name": "Naturalistic / Native",
            "principles": ["ecosystem_support", "low_maintenance", "seasonal_dynamics"],
            "plant_characteristics": {
                "structural": {
                    "native_species": True,
                    "wildlife_value": True
                },
                "accent": {
                    "native_perennials": True,
                    "pollinator_support": True
                },
                "groundcover": {
                    "native_groundlayers": True,
                    "meadow_aesthetic": True
                }
            },
            "spacing_style": "naturalized_drifts",
            "color_palette": ["varied_green", "gold", "purple", "native_blooms"]
        }
    }

    @classmethod
    def get_style(cls, style: DesignStyle) -> Dict:
        """Get style package details"""
        return cls.STYLES.get(style, cls.STYLES[DesignStyle.TRADITIONAL])

    @classmethod
    def get_plant_requirements(cls, style: DesignStyle, role: PlantRole) -> Dict:
        """Get plant requirements for a role within a style"""
        style_data = cls.get_style(style)
        role_key = role.value.replace("_softener", "").replace("_border", "")
        return style_data.get("plant_characteristics", {}).get(role_key, {})


class SpaceDesignModels:
    """
    Design models for different yard spaces.

    Training Insight: Each space type has distinct functional priorities.
    """

    SPACE_MODELS = {
        YardSpace.FRONT_YARD: {
            "name": "Front Yard - Curb Appeal",
            "primary_function": "First impression, architecture framing",
            "design_principles": ["entry_framing", "symmetry_or_balance", "structure_first"],
            "priority_roles": [
                PlantRole.FOUNDATION_SOFTENER,
                PlantRole.STRUCTURAL,
                PlantRole.ACCENT,
                PlantRole.EDGE_BORDER
            ],
            "training_insight": "Front-yard planting frames architecture, reinforces geometry. Structure first, color second.",
            "typical_layers": [PlantLayer.SHRUB, PlantLayer.HERBACEOUS, PlantLayer.GROUNDCOVER]
        },

        YardSpace.BACKYARD: {
            "name": "Backyard - Living Space",
            "primary_function": "Privacy, outdoor living, family use",
            "design_principles": ["privacy_screening", "vertical_hierarchy", "enclosure"],
            "priority_roles": [
                PlantRole.SCREENING,
                PlantRole.CANOPY,
                PlantRole.UNDERSTORY,
                PlantRole.GROUNDCOVER
            ],
            "training_insight": "Backyard planting is purpose-driven, privacy-oriented, layer-dependent for scale control.",
            "typical_layers": [PlantLayer.CANOPY, PlantLayer.UNDERSTORY, PlantLayer.SHRUB, PlantLayer.GROUNDCOVER]
        },

        YardSpace.SIDE_YARD: {
            "name": "Side Yard - Transition Zone",
            "primary_function": "Utility corridor, design continuity",
            "design_principles": ["repetition", "screening", "continuity"],
            "priority_roles": [
                PlantRole.SCREENING,
                PlantRole.GROUNDCOVER,
                PlantRole.STRUCTURAL
            ],
            "training_insight": "Side yards continue design language, control views, use simple repeatable plant masses.",
            "typical_layers": [PlantLayer.SHRUB, PlantLayer.GROUNDCOVER]
        }
    }

    @classmethod
    def get_space_model(cls, space: YardSpace) -> Dict:
        """Get design model for a yard space"""
        return cls.SPACE_MODELS.get(space, cls.SPACE_MODELS[YardSpace.FRONT_YARD])


class AutoSwapEngine:
    """
    Automatic plant substitution engine.

    Core Rule: Design intent stays constant. Plant species change based on site conditions.
    """

    @staticmethod
    def is_plant_compatible(plant: PlantRecommendation, conditions: SiteConditions) -> Tuple[bool, List[str]]:
        """
        Check if a plant is compatible with site conditions.

        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        issues = []

        # Zone check (hard fail)
        if conditions.usda_zone < plant.zone_min or conditions.usda_zone > plant.zone_max:
            issues.append(f"Zone {conditions.usda_zone} outside range {plant.zone_min}-{plant.zone_max}")

        # Sun check (hard fail)
        if conditions.sun_exposure not in plant.sun_options:
            issues.append(f"Requires {plant.sun_options}, site has {conditions.sun_exposure}")

        # Water check (hard fail)
        if conditions.water_profile not in plant.water_options:
            issues.append(f"Requires {plant.water_options}, site has {conditions.water_profile}")

        # Size check (hard fail)
        if plant.mature_height_ft > conditions.space_height_limit:
            issues.append(f"Mature height {plant.mature_height_ft}ft exceeds limit {conditions.space_height_limit}ft")

        if plant.mature_width_ft > conditions.space_width_limit:
            issues.append(f"Mature width {plant.mature_width_ft}ft exceeds limit {conditions.space_width_limit}ft")

        # Deer resistance (soft preference)
        if conditions.deer_pressure and not plant.deer_resistant:
            issues.append("Site has deer pressure, plant not deer resistant (warning)")

        return len([i for i in issues if "warning" not in i.lower()]) == 0, issues

    @staticmethod
    def calculate_match_score(plant: PlantRecommendation, conditions: SiteConditions, role: PlantRole) -> float:
        """
        Calculate how well a plant matches the requirements.

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        max_score = 0.0

        # Role match (critical)
        max_score += 30
        if plant.role == role:
            score += 30

        # Zone fit (prefer middle of range)
        max_score += 20
        zone_range = plant.zone_max - plant.zone_min
        if zone_range > 0:
            zone_position = (conditions.usda_zone - plant.zone_min) / zone_range
            if 0.25 <= zone_position <= 0.75:
                score += 20
            elif 0 <= zone_position <= 1:
                score += 10

        # Maintenance match
        max_score += 15
        maintenance_levels = {"low": 1, "medium": 2, "high": 3}
        plant_level = maintenance_levels.get(plant.maintenance_level, 2)
        site_level = maintenance_levels.get(conditions.maintenance_tolerance, 2)
        if plant_level <= site_level:
            score += 15
        elif plant_level == site_level + 1:
            score += 7

        # Drought tolerance bonus for dry sites
        max_score += 10
        if conditions.water_profile == "dry" and plant.drought_tolerant:
            score += 10
        elif conditions.water_profile != "dry":
            score += 5

        # Deer resistance bonus
        max_score += 10
        if conditions.deer_pressure and plant.deer_resistant:
            score += 10
        elif not conditions.deer_pressure:
            score += 5

        # Evergreen bonus for year-round structure
        max_score += 10
        if plant.evergreen and role in [PlantRole.STRUCTURAL, PlantRole.SCREENING]:
            score += 10
        elif not plant.evergreen:
            score += 5

        # Size efficiency (prefer plants that use space well without exceeding)
        max_score += 5
        height_efficiency = plant.mature_height_ft / conditions.space_height_limit
        if 0.5 <= height_efficiency <= 0.9:
            score += 5
        elif 0.3 <= height_efficiency < 0.5:
            score += 2

        return score / max_score if max_score > 0 else 0.0

    @classmethod
    def find_swap(
        cls,
        original_plant: PlantRecommendation,
        conditions: SiteConditions,
        plant_database: List[PlantRecommendation],
        top_n: int = 3
    ) -> List[Tuple[PlantRecommendation, float, str]]:
        """
        Find swap alternatives for a plant that doesn't work in the conditions.

        Returns:
            List of (plant, score, reason) tuples
        """
        candidates = []

        for plant in plant_database:
            if plant.botanical_name == original_plant.botanical_name:
                continue

            # Must be same role
            if plant.role != original_plant.role:
                continue

            # Check compatibility
            compatible, issues = cls.is_plant_compatible(plant, conditions)
            if not compatible:
                continue

            # Calculate match score
            score = cls.calculate_match_score(plant, conditions, original_plant.role)

            # Generate swap reason
            reason = cls._generate_swap_reason(original_plant, plant, conditions)

            candidates.append((plant, score, reason))

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)

        return candidates[:top_n]

    @staticmethod
    def _generate_swap_reason(original: PlantRecommendation, replacement: PlantRecommendation, conditions: SiteConditions) -> str:
        """Generate human-readable swap explanation"""
        reasons = []

        # Zone adaptation
        if conditions.usda_zone < original.zone_min:
            reasons.append(f"cold tolerant for zone {conditions.usda_zone}")
        elif conditions.usda_zone > original.zone_max:
            reasons.append(f"heat tolerant for zone {conditions.usda_zone}")

        # Sun adaptation
        if conditions.sun_exposure not in original.sun_options:
            reasons.append(f"thrives in {conditions.sun_exposure}")

        # Water adaptation
        if conditions.water_profile not in original.water_options:
            reasons.append(f"suited for {conditions.water_profile} conditions")

        # Size
        if original.mature_height_ft > conditions.space_height_limit:
            reasons.append(f"stays under {conditions.space_height_limit}ft height limit")

        if not reasons:
            reasons.append("better overall match for site conditions")

        return f"Selected {replacement.common_name} because it {', '.join(reasons)}"


class ProposalExplanationEngine:
    """
    Generate client-facing explanations for proposals.

    Template-based system for consistent, professional language.
    """

    @staticmethod
    def generate_design_intent(space: YardSpace, style: DesignStyle) -> str:
        """Generate design intent statement"""
        space_model = SpaceDesignModels.get_space_model(space)
        style_data = StylePackages.get_style(style)

        return (
            f"This planting plan is designed to create a cohesive, home-integrated landscape "
            f"with {space_model['primary_function'].lower()}. Following {style_data['name']} "
            f"design principles, the plan emphasizes {', '.join(style_data['principles'][:2])} "
            f"for year-round structure and seasonal interest."
        )

    @staticmethod
    def generate_site_constraints(conditions: SiteConditions) -> str:
        """Generate site constraints statement"""
        zone_str = f"{conditions.usda_zone}{conditions.zone_suffix}"

        statement = (
            f"Plant selections are matched to your property's conditions: "
            f"Zone {zone_str}, {conditions.sun_exposure} sun exposure, "
            f"{conditions.water_profile} moisture profile"
        )

        if conditions.space_height_limit < 20:
            statement += f", with height limits of {conditions.space_height_limit}ft"

        if conditions.deer_pressure:
            statement += ", accounting for deer pressure"

        return statement + "."

    @staticmethod
    def generate_swap_justification(
        original_name: str,
        replacement_name: str,
        role: PlantRole,
        reason: str
    ) -> str:
        """Generate swap justification for proposal"""
        return (
            f"We selected {replacement_name} instead of {original_name} to maintain "
            f"the same design role ({role.value.replace('_', ' ')}) while improving "
            f"performance under your site conditions. {reason}"
        )

    @staticmethod
    def generate_maintenance_statement(maintenance_level: str) -> str:
        """Generate maintenance expectation statement"""
        levels = {
            "low": "minimal care with occasional seasonal attention",
            "medium": "regular seasonal maintenance including pruning and cleanup",
            "high": "attentive care with frequent pruning, feeding, and monitoring"
        }

        description = levels.get(maintenance_level, levels["medium"])

        return (
            f"This plan is built to meet a {maintenance_level} maintenance level, "
            f"requiring {description}. Plants have been selected to match your "
            f"maintenance preferences and site conditions."
        )

    @staticmethod
    def generate_layer_explanation(layers: List[PlantLayer]) -> str:
        """Generate explanation of planting layers"""
        layer_descriptions = {
            PlantLayer.CANOPY: "overhead tree canopy for shade and structure",
            PlantLayer.UNDERSTORY: "mid-height trees and large shrubs for depth",
            PlantLayer.SHRUB: "backbone shrubs for year-round presence",
            PlantLayer.HERBACEOUS: "perennials and ornamental grasses for seasonal color",
            PlantLayer.GROUNDCOVER: "low-growing plants to unify and finish the design"
        }

        descriptions = [layer_descriptions[l] for l in layers if l in layer_descriptions]

        if len(descriptions) == 1:
            return f"This design features {descriptions[0]}."
        elif len(descriptions) == 2:
            return f"This design layers {descriptions[0]} with {descriptions[1]}."
        else:
            return (
                f"This design creates depth through multiple layers: "
                f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}."
            )


class HomePlantTrainer:
    """
    Main orchestrator for residential plant design.

    Capabilities:
    - Plant Role Matrix assignment
    - Zone/condition-aware plant selection
    - Style-based design packages
    - Auto-swap for climate adaptation
    - Client-ready proposal explanations
    """

    def __init__(self, plant_database: Optional[List[PlantRecommendation]] = None):
        """Initialize with optional plant database"""
        self.plant_database = plant_database or self._load_default_database()
        self.swap_engine = AutoSwapEngine()
        self.explanation_engine = ProposalExplanationEngine()
        print("[HomePlantTrainer] Initialized with plant database")

    def design_planting(
        self,
        zone: int,
        sun: str = "full",
        water: str = "average",
        space: str = "front_yard",
        style: str = "craftsman",
        height_limit: float = 20.0,
        width_limit: float = 10.0,
        maintenance: str = "medium",
        deer_pressure: bool = False,
        zone_suffix: str = ""
    ) -> Dict[str, Any]:
        """
        Create a complete planting design for a residential space.

        Args:
            zone: USDA hardiness zone (3-10)
            sun: Sun exposure (full, part, shade)
            water: Water profile (dry, average, wet)
            space: Yard space (front_yard, backyard, side_yard)
            style: Design style (traditional, farmhouse, craftsman, modern, cottage, naturalistic)
            height_limit: Maximum plant height in feet
            width_limit: Maximum plant width in feet
            maintenance: Maintenance tolerance (low, medium, high)
            deer_pressure: Whether deer are a concern
            zone_suffix: Zone suffix (a or b)

        Returns:
            Complete planting design with plants, explanations, and notes
        """
        print(f"\n[HomePlantTrainer] Creating {style} design for {space}...")
        print(f"  Zone: {zone}{zone_suffix}, Sun: {sun}, Water: {water}")

        # Build site conditions
        conditions = SiteConditions(
            usda_zone=zone,
            zone_suffix=zone_suffix,
            sun_exposure=sun,
            water_profile=water,
            space_height_limit=height_limit,
            space_width_limit=width_limit,
            maintenance_tolerance=maintenance,
            deer_pressure=deer_pressure
        )

        # Get space model and style
        yard_space = YardSpace(space)
        design_style = DesignStyle(style)
        space_model = SpaceDesignModels.get_space_model(yard_space)

        # Select plants for each priority role
        selected_plants = []
        for role in space_model["priority_roles"]:
            plants = self._select_plants_for_role(role, conditions, design_style)
            selected_plants.extend(plants)

        # Generate proposal explanations
        explanations = {
            "design_intent": self.explanation_engine.generate_design_intent(yard_space, design_style),
            "site_constraints": self.explanation_engine.generate_site_constraints(conditions),
            "maintenance": self.explanation_engine.generate_maintenance_statement(maintenance),
            "layers": self.explanation_engine.generate_layer_explanation(space_model["typical_layers"])
        }

        result = {
            "design": {
                "space": space,
                "style": style,
                "zone": f"{zone}{zone_suffix}",
                "conditions": {
                    "sun": sun,
                    "water": water,
                    "maintenance": maintenance
                }
            },
            "plants": [self._plant_to_dict(p) for p in selected_plants],
            "plant_summary": self._generate_plant_summary(selected_plants),
            "explanations": explanations,
            "design_notes": space_model["training_insight"],
            "timestamp": datetime.now().isoformat()
        }

        print(f"[HomePlantTrainer] Design complete with {len(selected_plants)} plants")
        return result

    def recommend_plants(
        self,
        role: str,
        zone: int,
        sun: str = "full",
        water: str = "average",
        height_limit: float = 20.0,
        width_limit: float = 10.0,
        count: int = 5
    ) -> List[Dict]:
        """
        Recommend plants for a specific role and conditions.

        Args:
            role: Plant role (structural, accent, screening, etc.)
            zone: USDA hardiness zone
            sun: Sun exposure
            water: Water profile
            height_limit: Maximum height
            width_limit: Maximum width
            count: Number of recommendations

        Returns:
            List of plant recommendations with scores
        """
        print(f"\n[HomePlantTrainer] Finding {role} plants for zone {zone}...")

        conditions = SiteConditions(
            usda_zone=zone,
            sun_exposure=sun,
            water_profile=water,
            space_height_limit=height_limit,
            space_width_limit=width_limit
        )

        plant_role = PlantRole(role)

        # Filter and score plants
        candidates = []
        for plant in self.plant_database:
            if plant.role != plant_role:
                continue

            compatible, _ = self.swap_engine.is_plant_compatible(plant, conditions)
            if not compatible:
                continue

            score = self.swap_engine.calculate_match_score(plant, conditions, plant_role)
            candidates.append((plant, score))

        # Sort by score
        candidates.sort(key=lambda x: x[1], reverse=True)

        results = []
        for plant, score in candidates[:count]:
            plant_dict = self._plant_to_dict(plant)
            plant_dict["match_score"] = round(score, 2)
            results.append(plant_dict)

        print(f"[HomePlantTrainer] Found {len(results)} matching plants")
        return results

    def swap_plant(
        self,
        plant_name: str,
        zone: int,
        sun: str = "full",
        water: str = "average",
        height_limit: float = 20.0,
        width_limit: float = 10.0
    ) -> Dict[str, Any]:
        """
        Find swap alternatives for a plant that doesn't work in conditions.

        Args:
            plant_name: Common or botanical name of plant to swap
            zone: Target USDA zone
            sun: Target sun exposure
            water: Target water profile
            height_limit: Maximum height allowed
            width_limit: Maximum width allowed

        Returns:
            Original plant info and list of alternatives
        """
        print(f"\n[HomePlantTrainer] Finding swaps for {plant_name} in zone {zone}...")

        # Find the original plant
        original = None
        for plant in self.plant_database:
            if plant_name.lower() in plant.common_name.lower() or \
               plant_name.lower() in plant.botanical_name.lower():
                original = plant
                break

        if not original:
            return {
                "error": f"Plant '{plant_name}' not found in database",
                "suggestion": "Try searching with a different name or check spelling"
            }

        conditions = SiteConditions(
            usda_zone=zone,
            sun_exposure=sun,
            water_profile=water,
            space_height_limit=height_limit,
            space_width_limit=width_limit
        )

        # Check if original works
        compatible, issues = self.swap_engine.is_plant_compatible(original, conditions)

        if compatible:
            return {
                "original": self._plant_to_dict(original),
                "compatible": True,
                "message": f"{original.common_name} works well in your conditions!",
                "alternatives": []
            }

        # Find swaps
        swaps = self.swap_engine.find_swap(original, conditions, self.plant_database)

        alternatives = []
        for plant, score, reason in swaps:
            alt = self._plant_to_dict(plant)
            alt["match_score"] = round(score, 2)
            alt["swap_reason"] = reason
            alt["justification"] = self.explanation_engine.generate_swap_justification(
                original.common_name,
                plant.common_name,
                original.role,
                reason
            )
            alternatives.append(alt)

        print(f"[HomePlantTrainer] Found {len(alternatives)} swap alternatives")

        return {
            "original": self._plant_to_dict(original),
            "compatible": False,
            "issues": issues,
            "alternatives": alternatives
        }

    def get_style_guide(self, style: str) -> Dict[str, Any]:
        """
        Get detailed style guide for a design style.

        Args:
            style: Design style name

        Returns:
            Style guide with principles, characteristics, and tips
        """
        design_style = DesignStyle(style)
        style_data = StylePackages.get_style(design_style)

        return {
            "name": style_data["name"],
            "principles": style_data["principles"],
            "spacing_style": style_data["spacing_style"],
            "color_palette": style_data["color_palette"],
            "plant_characteristics": style_data["plant_characteristics"],
            "tips": self._get_style_tips(design_style)
        }

    def get_space_guide(self, space: str) -> Dict[str, Any]:
        """
        Get design guide for a yard space.

        Args:
            space: Yard space (front_yard, backyard, side_yard)

        Returns:
            Space guide with priorities, layers, and insights
        """
        yard_space = YardSpace(space)
        model = SpaceDesignModels.get_space_model(yard_space)

        return {
            "name": model["name"],
            "primary_function": model["primary_function"],
            "design_principles": model["design_principles"],
            "priority_roles": [r.value for r in model["priority_roles"]],
            "typical_layers": [l.value for l in model["typical_layers"]],
            "design_insight": model["training_insight"]
        }

    def get_role_guide(self, role: str) -> Dict[str, Any]:
        """
        Get detailed guide for a plant role.

        Args:
            role: Plant role name

        Returns:
            Role guide with requirements and fallback options
        """
        plant_role = PlantRole(role)
        requirements = PlantRoleMatrix.get_role_requirements(plant_role)
        fallbacks = PlantRoleMatrix.get_fallback_roles(plant_role)

        return {
            "role": role,
            "description": requirements.get("description", ""),
            "primary_layer": requirements.get("layer", PlantLayer.SHRUB).value,
            "typical_forms": [f.value for f in requirements.get("typical_form", [])],
            "height_range_ft": requirements.get("height_range", (0, 10)),
            "special_requirements": {
                k: v for k, v in requirements.items()
                if k not in ["description", "layer", "typical_form", "height_range"]
            },
            "fallback_roles": [r.value for r in fallbacks]
        }

    # Private helper methods

    def _select_plants_for_role(
        self,
        role: PlantRole,
        conditions: SiteConditions,
        style: DesignStyle
    ) -> List[PlantRecommendation]:
        """Select best plants for a role given conditions and style"""
        candidates = []

        for plant in self.plant_database:
            if plant.role != role:
                continue

            compatible, _ = self.swap_engine.is_plant_compatible(plant, conditions)
            if not compatible:
                continue

            score = self.swap_engine.calculate_match_score(plant, conditions, role)
            candidates.append((plant, score))

        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top 2 for variety
        return [p for p, _ in candidates[:2]]

    def _plant_to_dict(self, plant: PlantRecommendation) -> Dict:
        """Convert plant recommendation to dictionary"""
        return {
            "botanical_name": plant.botanical_name,
            "common_name": plant.common_name,
            "role": plant.role.value,
            "layer": plant.layer.value,
            "form": plant.form.value,
            "size": {
                "height_ft": plant.mature_height_ft,
                "width_ft": plant.mature_width_ft
            },
            "hardiness": {
                "zone_min": plant.zone_min,
                "zone_max": plant.zone_max
            },
            "conditions": {
                "sun": plant.sun_options,
                "water": plant.water_options
            },
            "characteristics": {
                "evergreen": plant.evergreen,
                "seasonal_interest": plant.seasonal_interest,
                "maintenance": plant.maintenance_level,
                "deer_resistant": plant.deer_resistant,
                "drought_tolerant": plant.drought_tolerant
            },
            "design_notes": plant.design_notes
        }

    def _generate_plant_summary(self, plants: List[PlantRecommendation]) -> Dict:
        """Generate summary of selected plants"""
        return {
            "total_count": len(plants),
            "by_role": self._count_by_attribute(plants, "role"),
            "by_layer": self._count_by_attribute(plants, "layer"),
            "evergreen_count": sum(1 for p in plants if p.evergreen),
            "deciduous_count": sum(1 for p in plants if not p.evergreen)
        }

    def _count_by_attribute(self, plants: List[PlantRecommendation], attr: str) -> Dict[str, int]:
        """Count plants by an attribute"""
        counts = {}
        for plant in plants:
            value = getattr(plant, attr).value
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _get_style_tips(self, style: DesignStyle) -> List[str]:
        """Get design tips for a style"""
        tips = {
            DesignStyle.TRADITIONAL: [
                "Use formal shrub lines along foundation",
                "Maintain symmetry in entry plantings",
                "Prefer classic evergreen structure"
            ],
            DesignStyle.FARMHOUSE: [
                "Group plants in informal masses",
                "Mix native species for texture variety",
                "Allow plants to grow naturally without heavy pruning"
            ],
            DesignStyle.CRAFTSMAN: [
                "Layer evergreens for year-round structure",
                "Use plants that echo natural materials",
                "Emphasize horizontal lines in foundation plantings"
            ],
            DesignStyle.MODERN: [
                "Limit species palette to 3-5 plants",
                "Use repetition for visual impact",
                "Select plants with architectural forms"
            ],
            DesignStyle.COTTAGE: [
                "Layer plants densely for abundance",
                "Mix heights within beds",
                "Plan for continuous bloom sequence"
            ],
            DesignStyle.NATURALISTIC: [
                "Prioritize native species",
                "Plant in naturalized drifts",
                "Include plants for pollinators and wildlife"
            ]
        }
        return tips.get(style, [])

    def _load_default_database(self) -> List[PlantRecommendation]:
        """Load default plant database"""
        # Import from plant_database module
        from plant_database import get_plant_database
        return get_plant_database()


def main():
    """Demo usage of HomePlantTrainer"""
    print("=" * 60)
    print("Home Plant Trainer - Demo")
    print("=" * 60)

    trainer = HomePlantTrainer()

    # Example 1: Create front yard design
    print("\n--- Example 1: Front Yard Craftsman Design ---")
    result = trainer.design_planting(
        zone=7,
        sun="full",
        water="average",
        space="front_yard",
        style="craftsman",
        maintenance="medium"
    )
    print(f"\nDesign Intent: {result['explanations']['design_intent']}")
    print(f"Plants selected: {result['plant_summary']['total_count']}")

    # Example 2: Get plant recommendations
    print("\n\n--- Example 2: Structural Plant Recommendations ---")
    recommendations = trainer.recommend_plants(
        role="structural",
        zone=6,
        sun="part",
        water="average"
    )
    for rec in recommendations[:3]:
        print(f"  - {rec['common_name']} (score: {rec['match_score']})")

    # Example 3: Swap a plant
    print("\n\n--- Example 3: Plant Swap ---")
    swap_result = trainer.swap_plant(
        plant_name="boxwood",
        zone=4,
        sun="full"
    )
    if swap_result.get("alternatives"):
        print("Alternatives found:")
        for alt in swap_result["alternatives"][:2]:
            print(f"  - {alt['common_name']}: {alt['swap_reason']}")

    # Example 4: Get style guide
    print("\n\n--- Example 4: Modern Style Guide ---")
    style_guide = trainer.get_style_guide("modern")
    print(f"Style: {style_guide['name']}")
    print(f"Principles: {', '.join(style_guide['principles'])}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

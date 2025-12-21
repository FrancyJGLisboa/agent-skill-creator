#!/usr/bin/env python3
"""
Home Plant Trainer - Adaptive Residential Plant Design Advisor

A comprehensive plant-only design system for home landscapes.
Zone-aware, condition-driven plant selection with automatic species swapping.

Core Features:
- Plant Role Matrix (Structural, Accent, Screening, Foundation, Groundcover, Canopy, Understory)
- Adaptive zone/sun/water/size plant selection
- Style-based design packages (Traditional, Farmhouse, Craftsman, Modern)
- Auto-swap plant recommendations for any climate
- Client-facing explanation engine for proposals

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

import json
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Import companion modules
from utils.plant_database import PlantDatabase, Plant
from utils.design_advisor import DesignAdvisor, StylePackage


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class PlantRole(Enum):
    """Plant roles in the landscape design hierarchy."""
    STRUCTURAL = "structural"           # Backbone - holds design together year-round
    ACCENT = "accent"                   # Focal points, seasonal punch, "moments"
    SCREENING = "screening"             # Privacy, view control, buffering
    FOUNDATION_SOFTENER = "foundation"  # Reduces harsh lines of home base
    EDGE_BORDER = "edge"               # Clean bed lines, lawn transitions
    GROUNDCOVER = "groundcover"        # Covers soil, suppresses weeds, unifies
    CANOPY = "canopy"                  # Overhead structure, microclimate builder
    UNDERSTORY = "understory"          # Mid-layer for depth, seasonal interest


class PlantLayer(Enum):
    """Vertical layers in planting design."""
    CANOPY = "canopy"           # 20-60+ ft - overhead trees
    UNDERSTORY = "understory"   # 10-25 ft - small trees, large shrubs
    SHRUB = "shrub"             # 3-10 ft - primary shrub layer
    HERBACEOUS = "herbaceous"   # 1-4 ft - perennials, ornamental grasses
    GROUNDCOVER = "groundcover" # 2-18 in - low spreading plants


class SunExposure(Enum):
    """Sun exposure categories."""
    FULL = "full"       # 6+ hours direct sun
    PART = "part"       # 3-6 hours direct sun
    SHADE = "shade"     # Less than 3 hours direct sun


class WaterNeeds(Enum):
    """Water requirement categories."""
    DRY = "dry"         # Drought tolerant, minimal supplemental water
    AVERAGE = "average" # Moderate, typical garden watering
    WET = "wet"         # Moisture-loving, tolerates poor drainage


class SoilType(Enum):
    """Soil type categories."""
    CLAY = "clay"
    LOAM = "loam"
    SAND = "sand"
    ROCKY = "rocky"


class MaintenanceLevel(Enum):
    """Maintenance requirement levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DesignStyle(Enum):
    """Architectural/design style categories."""
    TRADITIONAL = "traditional"   # Colonial - formal, symmetric
    FARMHOUSE = "farmhouse"       # Informal, native, textured
    CRAFTSMAN = "craftsman"       # Layered, natural, horizontal
    MODERN = "modern"             # Minimal, repetition, architectural
    COTTAGE = "cottage"           # Abundant, romantic, informal
    NATURALISTIC = "naturalistic" # Native, meadow-like, ecological


class YardLocation(Enum):
    """Landscape location categories."""
    FRONT_YARD = "front_yard"
    BACKYARD = "backyard"
    SIDE_YARD = "side_yard"


# ============================================================================
# PLANT ROLE MATRIX
# ============================================================================

@dataclass
class PlantRoleSpec:
    """Specification for a plant role in the design hierarchy."""
    role: PlantRole
    layer: PlantLayer
    form_options: List[str]
    height_min_ft: float
    height_max_ft: float
    width_min_ft: float
    width_max_ft: float
    must_tolerate_pruning: bool
    typical_constraints: List[str]
    fallback_roles: List[PlantRole]
    description: str


# Master Plant Role Matrix - Universal across all zones
PLANT_ROLE_MATRIX: Dict[PlantRole, PlantRoleSpec] = {
    PlantRole.STRUCTURAL: PlantRoleSpec(
        role=PlantRole.STRUCTURAL,
        layer=PlantLayer.SHRUB,
        form_options=["rounded", "upright", "vase", "columnar"],
        height_min_ft=3.0,
        height_max_ft=8.0,
        width_min_ft=3.0,
        width_max_ft=6.0,
        must_tolerate_pruning=True,
        typical_constraints=["dense habit", "year-round interest", "reliable"],
        fallback_roles=[PlantRole.FOUNDATION_SOFTENER, PlantRole.SCREENING],
        description="Backbone plants that hold the design together year-round"
    ),
    PlantRole.ACCENT: PlantRoleSpec(
        role=PlantRole.ACCENT,
        layer=PlantLayer.HERBACEOUS,
        form_options=["mounding", "vertical", "weeping", "fountain"],
        height_min_ft=1.0,
        height_max_ft=6.0,
        width_min_ft=1.0,
        width_max_ft=4.0,
        must_tolerate_pruning=False,
        typical_constraints=["bloom priority", "texture interest", "seasonal impact"],
        fallback_roles=[PlantRole.STRUCTURAL],
        description="Focal points providing seasonal punch and visual moments"
    ),
    PlantRole.SCREENING: PlantRoleSpec(
        role=PlantRole.SCREENING,
        layer=PlantLayer.UNDERSTORY,
        form_options=["upright", "columnar", "dense"],
        height_min_ft=6.0,
        height_max_ft=25.0,
        width_min_ft=4.0,
        width_max_ft=12.0,
        must_tolerate_pruning=True,
        typical_constraints=["reliable", "dense growth", "fast establishing"],
        fallback_roles=[PlantRole.STRUCTURAL],
        description="Privacy, view control, and visual buffering"
    ),
    PlantRole.FOUNDATION_SOFTENER: PlantRoleSpec(
        role=PlantRole.FOUNDATION_SOFTENER,
        layer=PlantLayer.SHRUB,
        form_options=["rounded", "mounding", "spreading"],
        height_min_ft=2.0,
        height_max_ft=5.0,
        width_min_ft=2.0,
        width_max_ft=5.0,
        must_tolerate_pruning=True,
        typical_constraints=["must not block windows/vents", "clean habit"],
        fallback_roles=[PlantRole.STRUCTURAL, PlantRole.EDGE_BORDER],
        description="Reduces harsh architectural lines at home base"
    ),
    PlantRole.EDGE_BORDER: PlantRoleSpec(
        role=PlantRole.EDGE_BORDER,
        layer=PlantLayer.GROUNDCOVER,
        form_options=["low-mounding", "spreading", "tidy"],
        height_min_ft=0.5,
        height_max_ft=1.5,
        width_min_ft=1.0,
        width_max_ft=3.0,
        must_tolerate_pruning=False,
        typical_constraints=["must stay tidy", "clean edge"],
        fallback_roles=[PlantRole.GROUNDCOVER],
        description="Clean bed lines, lawn transitions, pathway definition"
    ),
    PlantRole.GROUNDCOVER: PlantRoleSpec(
        role=PlantRole.GROUNDCOVER,
        layer=PlantLayer.GROUNDCOVER,
        form_options=["spreading", "matting", "creeping"],
        height_min_ft=0.15,  # 2 inches
        height_max_ft=1.0,
        width_min_ft=1.0,
        width_max_ft=6.0,
        must_tolerate_pruning=False,
        typical_constraints=["weed suppression", "erosion control", "fill gaps"],
        fallback_roles=[PlantRole.EDGE_BORDER],
        description="Covers soil, suppresses weeds, unifies planting layers"
    ),
    PlantRole.CANOPY: PlantRoleSpec(
        role=PlantRole.CANOPY,
        layer=PlantLayer.CANOPY,
        form_options=["broad", "columnar", "vase", "rounded", "pyramidal"],
        height_min_ft=20.0,
        height_max_ft=60.0,
        width_min_ft=15.0,
        width_max_ft=40.0,
        must_tolerate_pruning=False,
        typical_constraints=["setback from structures", "utility clearance", "root space"],
        fallback_roles=[PlantRole.UNDERSTORY],
        description="Overhead structure, shade, and microclimate creation"
    ),
    PlantRole.UNDERSTORY: PlantRoleSpec(
        role=PlantRole.UNDERSTORY,
        layer=PlantLayer.UNDERSTORY,
        form_options=["layered", "vase", "rounded", "multi-stem"],
        height_min_ft=10.0,
        height_max_ft=25.0,
        width_min_ft=8.0,
        width_max_ft=20.0,
        must_tolerate_pruning=False,
        typical_constraints=["shade tolerance", "scale transition"],
        fallback_roles=[PlantRole.SCREENING, PlantRole.STRUCTURAL],
        description="Mid-layer for depth, seasonal interest, and scale control"
    ),
}


# ============================================================================
# SITE CONDITIONS
# ============================================================================

@dataclass
class SiteConditions:
    """Site-specific growing conditions for plant selection."""
    usda_zone: str                              # e.g., "6b", "7a", "8"
    sun_exposure: SunExposure
    water_profile: WaterNeeds
    soil_type: SoilType = SoilType.LOAM
    height_limit_ft: Optional[float] = None     # Max plant height allowed
    width_limit_ft: Optional[float] = None      # Max plant width allowed
    maintenance_level: MaintenanceLevel = MaintenanceLevel.MEDIUM
    wind_exposed: bool = False
    salt_exposure: bool = False                 # Coastal/road salt
    deer_pressure: bool = False

    def get_zone_number(self) -> int:
        """Extract numeric zone from USDA zone string."""
        zone_str = self.usda_zone.rstrip('ab')
        return int(zone_str)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "usda_zone": self.usda_zone,
            "sun_exposure": self.sun_exposure.value,
            "water_profile": self.water_profile.value,
            "soil_type": self.soil_type.value,
            "height_limit_ft": self.height_limit_ft,
            "width_limit_ft": self.width_limit_ft,
            "maintenance_level": self.maintenance_level.value,
            "wind_exposed": self.wind_exposed,
            "salt_exposure": self.salt_exposure,
            "deer_pressure": self.deer_pressure
        }


# ============================================================================
# DESIGN REQUEST
# ============================================================================

@dataclass
class DesignRequest:
    """A complete plant design request with all parameters."""
    location: YardLocation
    style: DesignStyle
    site_conditions: SiteConditions
    roles_needed: List[PlantRole]
    year_round_structure: bool = True
    seasonal_priority: Optional[str] = None  # "spring", "summer", "fall", "winter"
    wildlife_friendly: bool = False
    native_preference: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "location": self.location.value,
            "style": self.style.value,
            "site_conditions": self.site_conditions.to_dict(),
            "roles_needed": [r.value for r in self.roles_needed],
            "year_round_structure": self.year_round_structure,
            "seasonal_priority": self.seasonal_priority,
            "wildlife_friendly": self.wildlife_friendly,
            "native_preference": self.native_preference
        }


# ============================================================================
# PLANT SELECTION ENGINE
# ============================================================================

class PlantSelectionEngine:
    """
    Core engine for adaptive plant selection based on conditions.

    Implements the auto-swap rules:
    - Step A: Non-negotiable filters (hard fails)
    - Step B: Preference scoring (soft ranking)
    - Step C: Design integrity lock (role preservation)
    """

    def __init__(self, plant_db: PlantDatabase):
        self.plant_db = plant_db

    def select_plants_for_role(
        self,
        role: PlantRole,
        conditions: SiteConditions,
        style: Optional[DesignStyle] = None,
        count: int = 3
    ) -> List[Tuple[Plant, float, str]]:
        """
        Select plants for a specific role under given conditions.

        Returns list of (Plant, score, reasoning) tuples.
        """
        role_spec = PLANT_ROLE_MATRIX[role]
        candidates = []

        # Get all plants that match the role
        role_plants = self.plant_db.get_plants_by_role(role)

        for plant in role_plants:
            # Step A: Non-negotiable filters
            passes, fail_reason = self._check_hard_filters(plant, conditions, role_spec)
            if not passes:
                continue

            # Step B: Preference scoring
            score, score_reasons = self._calculate_preference_score(
                plant, conditions, style, role_spec
            )

            candidates.append((plant, score, " | ".join(score_reasons)))

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Return top candidates
        return candidates[:count]

    def _check_hard_filters(
        self,
        plant: Plant,
        conditions: SiteConditions,
        role_spec: PlantRoleSpec
    ) -> Tuple[bool, Optional[str]]:
        """
        Step A: Non-negotiable filters (hard fails).

        A plant is eligible only if:
        - USDA zone is within plant's range
        - Sun exposure matches
        - Water profile matches
        - Size is within limits
        """
        zone_num = conditions.get_zone_number()

        # Zone check
        if not (plant.zone_min <= zone_num <= plant.zone_max):
            return False, f"Zone {conditions.usda_zone} outside range {plant.zone_min}-{plant.zone_max}"

        # Sun check
        if conditions.sun_exposure.value not in plant.sun_tolerance:
            return False, f"Requires {conditions.sun_exposure.value} sun, plant tolerates {plant.sun_tolerance}"

        # Water check
        if conditions.water_profile.value not in plant.water_tolerance:
            return False, f"Requires {conditions.water_profile.value} water, plant tolerates {plant.water_tolerance}"

        # Size check - height
        if conditions.height_limit_ft:
            if plant.mature_height_ft > conditions.height_limit_ft:
                return False, f"Height {plant.mature_height_ft}ft exceeds limit {conditions.height_limit_ft}ft"

        # Size check - width
        if conditions.width_limit_ft:
            if plant.mature_width_ft > conditions.width_limit_ft:
                return False, f"Width {plant.mature_width_ft}ft exceeds limit {conditions.width_limit_ft}ft"

        # Role size constraints
        if plant.mature_height_ft < role_spec.height_min_ft:
            return False, f"Too short for {role_spec.role.value} role"
        if plant.mature_height_ft > role_spec.height_max_ft:
            return False, f"Too tall for {role_spec.role.value} role"

        return True, None

    def _calculate_preference_score(
        self,
        plant: Plant,
        conditions: SiteConditions,
        style: Optional[DesignStyle],
        role_spec: PlantRoleSpec
    ) -> Tuple[float, List[str]]:
        """
        Step B: Preference scoring (soft ranking).

        Rank plants by:
        - Role match (exact)
        - Evergreen match if year-round structure needed
        - Maintenance match
        - Deer resistance if flagged
        - Drought tolerance bonus
        - Soil tolerance bonus
        - Style match bonus
        """
        score = 0.0
        reasons = []

        # Base score for matching role
        score += 10.0
        reasons.append(f"Matches {role_spec.role.value} role")

        # Evergreen bonus for structural roles
        if plant.evergreen and role_spec.role in [
            PlantRole.STRUCTURAL, PlantRole.SCREENING, PlantRole.FOUNDATION_SOFTENER
        ]:
            score += 3.0
            reasons.append("Evergreen for year-round structure")

        # Maintenance match
        if plant.maintenance_level == conditions.maintenance_level.value:
            score += 2.0
            reasons.append(f"Matches {conditions.maintenance_level.value} maintenance")
        elif (conditions.maintenance_level == MaintenanceLevel.LOW and
              plant.maintenance_level == "medium"):
            score += 1.0
            reasons.append("Moderate maintenance acceptable")

        # Deer resistance
        if conditions.deer_pressure and plant.deer_resistant:
            score += 2.5
            reasons.append("Deer resistant")

        # Drought tolerance
        if conditions.water_profile == WaterNeeds.DRY and "dry" in plant.water_tolerance:
            score += 2.0
            reasons.append("Drought tolerant")

        # Soil tolerance
        if conditions.soil_type.value in plant.soil_tolerance:
            score += 1.5
            reasons.append(f"Tolerates {conditions.soil_type.value} soil")

        # Salt tolerance
        if conditions.salt_exposure and plant.salt_tolerant:
            score += 2.0
            reasons.append("Salt tolerant")

        # Native bonus
        if plant.native_regions:
            score += 1.0
            reasons.append("Native species")

        # Wildlife value
        if plant.wildlife_value:
            score += 0.5
            reasons.append("Wildlife habitat value")

        # Style match bonus (if style specified)
        if style and style.value in plant.style_tags:
            score += 2.0
            reasons.append(f"Matches {style.value} style")

        # Form match bonus
        if plant.form in role_spec.form_options:
            score += 1.5
            reasons.append(f"Form ({plant.form}) fits role")

        return score, reasons

    def find_swap_alternatives(
        self,
        original_plant_name: str,
        conditions: SiteConditions,
        count: int = 3
    ) -> List[Tuple[Plant, float, str]]:
        """
        Find alternative plants to swap for one that doesn't work.

        Maintains same role while adapting to new conditions.
        """
        # Find the original plant
        original = self.plant_db.get_plant_by_name(original_plant_name)
        if not original:
            return []

        # Get the primary role
        if not original.roles:
            return []

        primary_role = PlantRole(original.roles[0])

        # Find alternatives for same role
        alternatives = self.select_plants_for_role(
            role=primary_role,
            conditions=conditions,
            count=count + 1  # Get extra in case original is included
        )

        # Filter out the original plant
        alternatives = [
            (plant, score, reason)
            for plant, score, reason in alternatives
            if plant.common_name.lower() != original_plant_name.lower()
        ]

        return alternatives[:count]


# ============================================================================
# DESIGN BUILDER
# ============================================================================

class DesignBuilder:
    """
    Builds complete planting designs based on requests.

    Integrates:
    - Plant Role Matrix
    - Site conditions
    - Style packages
    - Selection engine
    """

    def __init__(self, plant_db: PlantDatabase, design_advisor: DesignAdvisor):
        self.plant_db = plant_db
        self.design_advisor = design_advisor
        self.selection_engine = PlantSelectionEngine(plant_db)

    def build_design(self, request: DesignRequest) -> Dict[str, Any]:
        """
        Build a complete planting design for the request.

        Returns a structured design with:
        - Plant selections by role
        - Design intent explanation
        - Site constraints acknowledgment
        - Maintenance guidance
        - Seasonal interest summary
        """
        design = {
            "design_intent": self._generate_design_intent(request),
            "site_constraints": request.site_conditions.to_dict(),
            "style": request.style.value,
            "location": request.location.value,
            "plant_selections": {},
            "seasonal_timeline": {},
            "maintenance_summary": "",
            "client_explanation": ""
        }

        # Get style package
        style_package = self.design_advisor.get_style_package(request.style)

        # Select plants for each required role
        for role in request.roles_needed:
            selections = self.selection_engine.select_plants_for_role(
                role=role,
                conditions=request.site_conditions,
                style=request.style,
                count=3
            )

            role_plants = []
            for plant, score, reasoning in selections:
                role_plants.append({
                    "plant_name": plant.common_name,
                    "botanical_name": plant.botanical_name,
                    "form": plant.form,
                    "mature_size": f"{plant.mature_height_ft}H x {plant.mature_width_ft}W ft",
                    "score": round(score, 1),
                    "selection_reasoning": reasoning,
                    "seasonal_interest": plant.seasonal_interest,
                    "maintenance": plant.maintenance_level
                })

            design["plant_selections"][role.value] = role_plants

        # Generate seasonal timeline
        design["seasonal_timeline"] = self._build_seasonal_timeline(design["plant_selections"])

        # Generate maintenance summary
        design["maintenance_summary"] = self._generate_maintenance_summary(
            design["plant_selections"],
            request.site_conditions.maintenance_level
        )

        # Generate client explanation
        design["client_explanation"] = self.design_advisor.generate_proposal_explanation(
            request, design
        )

        return design

    def _generate_design_intent(self, request: DesignRequest) -> str:
        """Generate a design intent statement."""
        location_phrases = {
            YardLocation.FRONT_YARD: "front yard with curb appeal focus",
            YardLocation.BACKYARD: "backyard living space",
            YardLocation.SIDE_YARD: "side yard transition zone"
        }

        style_phrases = {
            DesignStyle.TRADITIONAL: "formal, balanced aesthetic",
            DesignStyle.FARMHOUSE: "informal, naturalistic character",
            DesignStyle.CRAFTSMAN: "layered, natural material harmony",
            DesignStyle.MODERN: "minimalist, architectural clarity",
            DesignStyle.COTTAGE: "abundant, romantic abundance",
            DesignStyle.NATURALISTIC: "ecological, native planting"
        }

        intent = (
            f"This planting design creates a {location_phrases[request.location]} "
            f"with {style_phrases[request.style]}. "
            f"Plant selections are optimized for Zone {request.site_conditions.usda_zone}, "
            f"{request.site_conditions.sun_exposure.value} sun exposure, "
            f"and {request.site_conditions.water_profile.value} water conditions."
        )

        if request.year_round_structure:
            intent += " Year-round structure is prioritized through evergreen selections."

        if request.wildlife_friendly:
            intent += " Wildlife habitat value is incorporated."

        if request.native_preference:
            intent += " Native and regionally-adapted species are favored."

        return intent

    def _build_seasonal_timeline(self, plant_selections: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """Build a seasonal interest timeline from selections."""
        timeline = {
            "spring": [],
            "summer": [],
            "fall": [],
            "winter": []
        }

        for role, plants in plant_selections.items():
            for plant_info in plants:
                seasonal = plant_info.get("seasonal_interest", {})
                for season, interest in seasonal.items():
                    if interest and season in timeline:
                        timeline[season].append(
                            f"{plant_info['plant_name']}: {interest}"
                        )

        return timeline

    def _generate_maintenance_summary(
        self,
        plant_selections: Dict[str, List[Dict]],
        target_level: MaintenanceLevel
    ) -> str:
        """Generate maintenance guidance summary."""
        maintenance_tasks = []

        for role, plants in plant_selections.items():
            for plant_info in plants:
                level = plant_info.get("maintenance", "medium")
                if level == "high":
                    maintenance_tasks.append(
                        f"- {plant_info['plant_name']} requires regular attention"
                    )

        summary = (
            f"This design targets {target_level.value} maintenance level. "
        )

        if maintenance_tasks:
            summary += "Notable maintenance items:\n" + "\n".join(maintenance_tasks)
        else:
            summary += "All selections align with maintenance goals."

        return summary


# ============================================================================
# MAIN INTERFACE
# ============================================================================

class HomePlantTrainer:
    """
    Main interface for the Home Plant Trainer skill.

    Provides:
    - Complete design generation
    - Plant role recommendations
    - Plant swap alternatives
    - Style-based guidance
    - Proposal explanations
    """

    def __init__(self):
        self.plant_db = PlantDatabase()
        self.design_advisor = DesignAdvisor()
        self.design_builder = DesignBuilder(self.plant_db, self.design_advisor)
        self.selection_engine = PlantSelectionEngine(self.plant_db)

    def create_design(
        self,
        location: str,
        style: str,
        zone: str,
        sun: str,
        water: str,
        roles: Optional[List[str]] = None,
        height_limit: Optional[float] = None,
        width_limit: Optional[float] = None,
        maintenance: str = "medium",
        year_round: bool = True,
        wildlife: bool = False,
        native: bool = False
    ) -> Dict[str, Any]:
        """
        Create a complete planting design.

        Args:
            location: "front_yard", "backyard", or "side_yard"
            style: "traditional", "farmhouse", "craftsman", "modern", etc.
            zone: USDA zone like "6b", "7a", "8"
            sun: "full", "part", or "shade"
            water: "dry", "average", or "wet"
            roles: List of roles needed (defaults to standard set for location)
            height_limit: Maximum plant height in feet
            width_limit: Maximum plant width in feet
            maintenance: "low", "medium", or "high"
            year_round: Whether to prioritize year-round structure
            wildlife: Whether to favor wildlife-friendly plants
            native: Whether to prefer native species

        Returns:
            Complete design dictionary with selections and explanations
        """
        # Parse enums
        location_enum = YardLocation(location)
        style_enum = DesignStyle(style)
        sun_enum = SunExposure(sun)
        water_enum = WaterNeeds(water)
        maintenance_enum = MaintenanceLevel(maintenance)

        # Default roles by location if not specified
        if roles is None:
            roles = self._get_default_roles(location_enum)

        role_enums = [PlantRole(r) for r in roles]

        # Build site conditions
        conditions = SiteConditions(
            usda_zone=zone,
            sun_exposure=sun_enum,
            water_profile=water_enum,
            height_limit_ft=height_limit,
            width_limit_ft=width_limit,
            maintenance_level=maintenance_enum
        )

        # Build request
        request = DesignRequest(
            location=location_enum,
            style=style_enum,
            site_conditions=conditions,
            roles_needed=role_enums,
            year_round_structure=year_round,
            wildlife_friendly=wildlife,
            native_preference=native
        )

        # Generate design
        return self.design_builder.build_design(request)

    def get_plants_for_role(
        self,
        role: str,
        zone: str,
        sun: str,
        water: str,
        style: Optional[str] = None,
        height_limit: Optional[float] = None,
        width_limit: Optional[float] = None,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get plant recommendations for a specific role.

        Args:
            role: Plant role (structural, accent, screening, etc.)
            zone: USDA zone
            sun: Sun exposure
            water: Water needs
            style: Optional design style filter
            height_limit: Max height constraint
            width_limit: Max width constraint
            count: Number of recommendations to return

        Returns:
            List of plant recommendations with scores and reasoning
        """
        role_enum = PlantRole(role)

        conditions = SiteConditions(
            usda_zone=zone,
            sun_exposure=SunExposure(sun),
            water_profile=WaterNeeds(water),
            height_limit_ft=height_limit,
            width_limit_ft=width_limit
        )

        style_enum = DesignStyle(style) if style else None

        selections = self.selection_engine.select_plants_for_role(
            role=role_enum,
            conditions=conditions,
            style=style_enum,
            count=count
        )

        results = []
        for plant, score, reasoning in selections:
            results.append({
                "plant_name": plant.common_name,
                "botanical_name": plant.botanical_name,
                "form": plant.form,
                "size": f"{plant.mature_height_ft}H x {plant.mature_width_ft}W ft",
                "score": round(score, 1),
                "reasoning": reasoning,
                "evergreen": plant.evergreen,
                "seasonal_interest": plant.seasonal_interest
            })

        return results

    def swap_plant(
        self,
        plant_name: str,
        zone: str,
        sun: str,
        water: str,
        height_limit: Optional[float] = None,
        width_limit: Optional[float] = None,
        count: int = 3
    ) -> Dict[str, Any]:
        """
        Find alternative plants to swap for one that won't work.

        Args:
            plant_name: Name of plant to replace
            zone: Target USDA zone
            sun: Sun exposure at site
            water: Water conditions at site
            height_limit: Max height allowed
            width_limit: Max width allowed
            count: Number of alternatives to return

        Returns:
            Original plant info and list of alternatives
        """
        conditions = SiteConditions(
            usda_zone=zone,
            sun_exposure=SunExposure(sun),
            water_profile=WaterNeeds(water),
            height_limit_ft=height_limit,
            width_limit_ft=width_limit
        )

        original = self.plant_db.get_plant_by_name(plant_name)

        alternatives = self.selection_engine.find_swap_alternatives(
            original_plant_name=plant_name,
            conditions=conditions,
            count=count
        )

        result = {
            "original_plant": plant_name,
            "original_info": None,
            "swap_reason": f"Finding alternatives for Zone {zone}, {sun} sun, {water} water",
            "alternatives": []
        }

        if original:
            result["original_info"] = {
                "botanical_name": original.botanical_name,
                "roles": original.roles,
                "zone_range": f"{original.zone_min}-{original.zone_max}",
                "sun": original.sun_tolerance,
                "water": original.water_tolerance
            }

        for plant, score, reasoning in alternatives:
            result["alternatives"].append({
                "plant_name": plant.common_name,
                "botanical_name": plant.botanical_name,
                "form": plant.form,
                "size": f"{plant.mature_height_ft}H x {plant.mature_width_ft}W ft",
                "match_score": round(score, 1),
                "why_it_works": reasoning
            })

        return result

    def get_style_guide(self, style: str) -> Dict[str, Any]:
        """
        Get the design guide for a specific style.

        Args:
            style: Design style name

        Returns:
            Style package with principles and plant preferences
        """
        style_enum = DesignStyle(style)
        package = self.design_advisor.get_style_package(style_enum)

        return {
            "style": style,
            "description": package.description,
            "principles": package.principles,
            "form_preferences": package.form_preferences,
            "color_palette": package.color_palette,
            "spacing_approach": package.spacing_approach,
            "example_plants": package.example_plants
        }

    def get_role_specification(self, role: str) -> Dict[str, Any]:
        """
        Get the specification for a plant role.

        Args:
            role: Plant role name

        Returns:
            Role specification with size ranges and requirements
        """
        role_enum = PlantRole(role)
        spec = PLANT_ROLE_MATRIX[role_enum]

        return {
            "role": role,
            "description": spec.description,
            "typical_layer": spec.layer.value,
            "form_options": spec.form_options,
            "height_range_ft": f"{spec.height_min_ft}-{spec.height_max_ft}",
            "width_range_ft": f"{spec.width_min_ft}-{spec.width_max_ft}",
            "must_tolerate_pruning": spec.must_tolerate_pruning,
            "typical_constraints": spec.typical_constraints,
            "fallback_roles": [r.value for r in spec.fallback_roles]
        }

    def _get_default_roles(self, location: YardLocation) -> List[str]:
        """Get default roles for a yard location."""
        if location == YardLocation.FRONT_YARD:
            return ["structural", "foundation", "accent", "groundcover"]
        elif location == YardLocation.BACKYARD:
            return ["canopy", "screening", "structural", "accent", "groundcover"]
        elif location == YardLocation.SIDE_YARD:
            return ["screening", "structural", "groundcover"]
        return ["structural", "accent"]


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main entry point for CLI usage."""
    trainer = HomePlantTrainer()

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    if command == "design":
        # Example: python main.py design front_yard craftsman 7a full average
        if len(sys.argv) < 7:
            print("Usage: design <location> <style> <zone> <sun> <water>")
            return

        design = trainer.create_design(
            location=sys.argv[2],
            style=sys.argv[3],
            zone=sys.argv[4],
            sun=sys.argv[5],
            water=sys.argv[6]
        )
        print(json.dumps(design, indent=2))

    elif command == "role":
        # Example: python main.py role structural 6b full average
        if len(sys.argv) < 6:
            print("Usage: role <role> <zone> <sun> <water>")
            return

        plants = trainer.get_plants_for_role(
            role=sys.argv[2],
            zone=sys.argv[3],
            sun=sys.argv[4],
            water=sys.argv[5]
        )
        print(json.dumps(plants, indent=2))

    elif command == "swap":
        # Example: python main.py swap "Japanese Maple" 5a full dry
        if len(sys.argv) < 6:
            print("Usage: swap <plant_name> <zone> <sun> <water>")
            return

        alternatives = trainer.swap_plant(
            plant_name=sys.argv[2],
            zone=sys.argv[3],
            sun=sys.argv[4],
            water=sys.argv[5]
        )
        print(json.dumps(alternatives, indent=2))

    elif command == "style":
        # Example: python main.py style craftsman
        if len(sys.argv) < 3:
            print("Usage: style <style_name>")
            return

        guide = trainer.get_style_guide(sys.argv[2])
        print(json.dumps(guide, indent=2))

    elif command == "rolespec":
        # Example: python main.py rolespec structural
        if len(sys.argv) < 3:
            print("Usage: rolespec <role_name>")
            return

        spec = trainer.get_role_specification(sys.argv[2])
        print(json.dumps(spec, indent=2))

    else:
        print_help()


def print_help():
    """Print usage help."""
    help_text = """
Home Plant Trainer - Adaptive Residential Plant Design Advisor

Commands:
  design <location> <style> <zone> <sun> <water>
    Create a complete planting design
    Example: design front_yard craftsman 7a full average

  role <role> <zone> <sun> <water>
    Get plant recommendations for a specific role
    Example: role structural 6b full average

  swap <plant_name> <zone> <sun> <water>
    Find alternatives for a plant that won't work
    Example: swap "Japanese Maple" 5a full dry

  style <style_name>
    Get design guide for a style
    Example: style farmhouse

  rolespec <role_name>
    Get specification for a plant role
    Example: rolespec screening

Locations: front_yard, backyard, side_yard
Styles: traditional, farmhouse, craftsman, modern, cottage, naturalistic
Roles: structural, accent, screening, foundation, edge, groundcover, canopy, understory
Sun: full, part, shade
Water: dry, average, wet
"""
    print(help_text)


if __name__ == "__main__":
    main()

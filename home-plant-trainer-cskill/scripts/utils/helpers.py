"""
Utility helpers for Home Plant Trainer

Common functions for validation, formatting, and data handling.
"""

from typing import List, Dict, Any, Optional, Tuple
import re


def validate_zone(zone: Any) -> Tuple[bool, str]:
    """
    Validate USDA hardiness zone input.

    Args:
        zone: Zone value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        zone_num = int(zone)
        if 1 <= zone_num <= 13:
            return True, ""
        return False, f"Zone must be between 1 and 13, got {zone_num}"
    except (ValueError, TypeError):
        return False, f"Zone must be a number, got {type(zone).__name__}"


def validate_sun_exposure(sun: str) -> Tuple[bool, str]:
    """
    Validate sun exposure input.

    Args:
        sun: Sun exposure value

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_options = ["full", "part", "shade"]
    sun_lower = sun.lower().strip()

    if sun_lower in valid_options:
        return True, ""

    # Try to normalize common variations
    if sun_lower in ["full sun", "full-sun"]:
        return True, ""
    if sun_lower in ["part sun", "part shade", "partial", "partial shade"]:
        return True, ""
    if sun_lower in ["deep shade", "full shade"]:
        return True, ""

    return False, f"Sun must be one of {valid_options}, got '{sun}'"


def validate_water_profile(water: str) -> Tuple[bool, str]:
    """
    Validate water profile input.

    Args:
        water: Water profile value

    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_options = ["dry", "average", "wet"]
    water_lower = water.lower().strip()

    if water_lower in valid_options:
        return True, ""

    # Normalize variations
    if water_lower in ["drought", "xeric", "low water"]:
        return True, ""
    if water_lower in ["normal", "medium", "moderate"]:
        return True, ""
    if water_lower in ["moist", "boggy", "high water"]:
        return True, ""

    return False, f"Water must be one of {valid_options}, got '{water}'"


def normalize_sun_exposure(sun: str) -> str:
    """
    Normalize sun exposure input to standard values.

    Args:
        sun: Raw sun exposure input

    Returns:
        Normalized value (full, part, or shade)
    """
    sun_lower = sun.lower().strip()

    if sun_lower in ["full", "full sun", "full-sun"]:
        return "full"
    if sun_lower in ["part", "part sun", "part shade", "partial", "partial shade", "dappled"]:
        return "part"
    if sun_lower in ["shade", "deep shade", "full shade"]:
        return "shade"

    return "full"  # Default


def normalize_water_profile(water: str) -> str:
    """
    Normalize water profile input to standard values.

    Args:
        water: Raw water profile input

    Returns:
        Normalized value (dry, average, or wet)
    """
    water_lower = water.lower().strip()

    if water_lower in ["dry", "drought", "xeric", "low water", "low"]:
        return "dry"
    if water_lower in ["average", "normal", "medium", "moderate"]:
        return "average"
    if water_lower in ["wet", "moist", "boggy", "high water", "high"]:
        return "wet"

    return "average"  # Default


def normalize_style(style: str) -> str:
    """
    Normalize style input to standard values.

    Args:
        style: Raw style input

    Returns:
        Normalized style value
    """
    style_lower = style.lower().strip()

    # Map variations to standard names
    style_map = {
        "traditional": ["traditional", "classic", "formal"],
        "colonial": ["colonial", "georgian", "federal"],
        "farmhouse": ["farmhouse", "country", "rural", "rustic"],
        "craftsman": ["craftsman", "bungalow", "arts and crafts", "arts & crafts"],
        "modern": ["modern", "contemporary", "minimalist", "mid-century"],
        "cottage": ["cottage", "english garden", "romantic"],
        "naturalistic": ["naturalistic", "native", "prairie", "meadow", "eco"]
    }

    for standard, variations in style_map.items():
        if style_lower in variations:
            return standard

    return "traditional"  # Default


def normalize_space(space: str) -> str:
    """
    Normalize yard space input to standard values.

    Args:
        space: Raw space input

    Returns:
        Normalized space value
    """
    space_lower = space.lower().strip().replace(" ", "_")

    space_map = {
        "front_yard": ["front_yard", "front", "frontyard", "curb", "entry"],
        "backyard": ["backyard", "back_yard", "back", "rear", "patio_area"],
        "side_yard": ["side_yard", "sideyard", "side", "corridor", "passage"]
    }

    for standard, variations in space_map.items():
        if space_lower in variations:
            return standard

    return "front_yard"  # Default


def parse_zone_string(zone_str: str) -> Tuple[int, str]:
    """
    Parse zone string that may include suffix (e.g., "7a", "7b").

    Args:
        zone_str: Zone string like "7", "7a", "7b"

    Returns:
        Tuple of (zone_number, suffix)
    """
    zone_str = str(zone_str).strip().lower()

    # Check for suffix
    match = re.match(r"^(\d+)([ab])?$", zone_str)
    if match:
        zone_num = int(match.group(1))
        suffix = match.group(2) or ""
        return zone_num, suffix

    # Try to extract just the number
    match = re.search(r"\d+", zone_str)
    if match:
        return int(match.group()), ""

    return 7, ""  # Default to zone 7


def format_plant_name(botanical: str, common: str) -> str:
    """
    Format plant name for display.

    Args:
        botanical: Botanical name
        common: Common name

    Returns:
        Formatted string
    """
    return f"{common} ({botanical})"


def format_size(height_ft: float, width_ft: float) -> str:
    """
    Format plant size for display.

    Args:
        height_ft: Height in feet
        width_ft: Width in feet

    Returns:
        Formatted size string
    """
    return f"{height_ft:.0f}' H x {width_ft:.0f}' W"


def format_zone_range(zone_min: int, zone_max: int) -> str:
    """
    Format zone range for display.

    Args:
        zone_min: Minimum zone
        zone_max: Maximum zone

    Returns:
        Formatted zone range
    """
    if zone_min == zone_max:
        return f"Zone {zone_min}"
    return f"Zones {zone_min}-{zone_max}"


def format_plant_list(plants: List[Dict], include_details: bool = False) -> str:
    """
    Format a list of plants for text output.

    Args:
        plants: List of plant dictionaries
        include_details: Whether to include full details

    Returns:
        Formatted string
    """
    lines = []

    for i, plant in enumerate(plants, 1):
        name = format_plant_name(
            plant.get("botanical_name", ""),
            plant.get("common_name", "")
        )

        if include_details:
            size = format_size(
                plant.get("size", {}).get("height_ft", 0),
                plant.get("size", {}).get("width_ft", 0)
            )
            zones = format_zone_range(
                plant.get("hardiness", {}).get("zone_min", 0),
                plant.get("hardiness", {}).get("zone_max", 0)
            )
            role = plant.get("role", "").replace("_", " ").title()

            lines.append(f"{i}. {name}")
            lines.append(f"   Role: {role} | Size: {size} | {zones}")
        else:
            lines.append(f"{i}. {name}")

    return "\n".join(lines)


def calculate_seasonal_coverage(plants: List[Dict]) -> Dict[str, List[str]]:
    """
    Calculate which plants provide interest in each season.

    Args:
        plants: List of plant dictionaries

    Returns:
        Dictionary mapping seasons to plant names
    """
    seasons = {
        "spring": [],
        "summer": [],
        "fall": [],
        "winter": []
    }

    for plant in plants:
        interests = plant.get("characteristics", {}).get("seasonal_interest", [])
        name = plant.get("common_name", "Unknown")

        for season in interests:
            if season in seasons:
                seasons[season].append(name)

    return seasons


def generate_spacing_guidance(role: str, form: str) -> str:
    """
    Generate spacing guidance based on plant role and form.

    Args:
        role: Plant role
        form: Plant form

    Returns:
        Spacing guidance string
    """
    guidance = {
        "structural": "Space at 2/3 of mature width for mass effect, full width for specimens",
        "accent": "Space at full mature width to highlight individual form",
        "screening": "Space at 1/2 to 2/3 of mature width for privacy",
        "foundation_softener": "Space at 2/3 of mature width, offset from foundation by 3'",
        "edge_border": "Space at 1/2 mature width for continuous edge",
        "groundcover": "Space at 1/2 to 2/3 mature width for quick coverage",
        "canopy": "Space at full mature width minimum, consider views",
        "understory": "Space at 2/3 mature width, consider layering"
    }

    return guidance.get(role, "Space at mature width")


def get_maintenance_summary(plants: List[Dict]) -> Dict[str, Any]:
    """
    Generate maintenance summary for a plant list.

    Args:
        plants: List of plant dictionaries

    Returns:
        Maintenance summary dictionary
    """
    levels = {"low": 0, "medium": 0, "high": 0}
    evergreen_count = 0
    deciduous_count = 0

    for plant in plants:
        level = plant.get("characteristics", {}).get("maintenance", "medium")
        levels[level] = levels.get(level, 0) + 1

        if plant.get("characteristics", {}).get("evergreen", False):
            evergreen_count += 1
        else:
            deciduous_count += 1

    # Determine overall level
    if levels["high"] > len(plants) / 3:
        overall = "high"
    elif levels["low"] > len(plants) / 2:
        overall = "low"
    else:
        overall = "medium"

    tasks = []
    if deciduous_count > 0:
        tasks.append("Fall leaf cleanup")
    if levels["high"] > 0 or levels["medium"] > 0:
        tasks.append("Spring and fall pruning")
    if any(p.get("characteristics", {}).get("drought_tolerant", False) is False for p in plants):
        tasks.append("Regular watering during establishment")
    tasks.append("Annual mulching")

    return {
        "overall_level": overall,
        "by_level": levels,
        "evergreen_vs_deciduous": {
            "evergreen": evergreen_count,
            "deciduous": deciduous_count
        },
        "typical_tasks": tasks
    }

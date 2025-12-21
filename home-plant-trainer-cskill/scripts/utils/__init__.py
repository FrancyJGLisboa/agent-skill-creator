"""
Home Plant Trainer Utilities

Provides:
- PlantDatabase: Comprehensive plant data with zone/condition/role attributes
- DesignAdvisor: Style packages and proposal explanation engine
"""

from .plant_database import PlantDatabase, Plant
from .design_advisor import DesignAdvisor, StylePackage

__all__ = ['PlantDatabase', 'Plant', 'DesignAdvisor', 'StylePackage']

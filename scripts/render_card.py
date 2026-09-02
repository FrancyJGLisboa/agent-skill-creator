#!/usr/bin/env python3
"""Compatibility entrypoint for the generated Belief Card renderer."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).parents[1] / "output" / "belief-card-explainer-skill" / "scripts" / "render_card.py"), run_name="__main__")

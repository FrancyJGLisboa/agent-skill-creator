from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from run_phase1_semantic_recon import run


def test_phase_one_wrapper_emits_scope_and_skips_non_required_recon(tmp_path):
    skill = tmp_path / "skill"; skill.mkdir()
    (skill / "discovery.json").write_text(json.dumps({"data_interfaces": {"applies": False}}))
    assert run(skill) == {"status": "RESUMED", "reason": "Semantic Recon not required"}


def test_phase_one_wrapper_requires_discovery(tmp_path):
    assert run(tmp_path) == {"status": "BLOCKED_NO_DISCOVERY", "detail": str(tmp_path / "discovery.json")}

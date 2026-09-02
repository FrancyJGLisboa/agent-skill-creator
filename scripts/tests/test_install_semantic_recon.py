"""Regression checks for the optional pinned Semantic Recon installer."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).parent.parent.parent
INSTALLER = ROOT / "install.sh"
PIN = "78234a37ebfff4b046e299d703b9b1cf39133600"


def test_installer_documents_and_previews_the_optional_pinned_dependency() -> None:
    source = INSTALLER.read_text(encoding="utf-8")

    assert 'SEMANTIC_RECON_COMMIT="' + PIN + '"' in source
    assert "--with-semantic-recon)" in source
    assert 'git -C "$SEMANTIC_RECON_DIR" fetch --depth 1 origin "$SEMANTIC_RECON_COMMIT"' in source
    assert 'git -C "$SEMANTIC_RECON_DIR" checkout --detach "$SEMANTIC_RECON_COMMIT"' in source

    result = subprocess.run(
        ["sh", str(INSTALLER), "--dry-run", "--with-semantic-recon"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Would install semantic-recon" in result.stdout
    assert PIN in result.stdout


def test_default_dry_run_selects_semantic_recon() -> None:
    result = subprocess.run(
        ["sh", str(INSTALLER), "--dry-run"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "Would install semantic-recon" in result.stdout


def test_explicit_opt_out_skips_semantic_recon() -> None:
    result = subprocess.run(
        ["sh", str(INSTALLER), "--dry-run", "--without-semantic-recon"],
        cwd=ROOT, check=True, text=True, capture_output=True,
    )
    assert "semantic-recon" not in result.stdout.lower()

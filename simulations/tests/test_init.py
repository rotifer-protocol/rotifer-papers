"""C.1 — Repository initialization tests.

TDD red phase: passes once the project is correctly bootstrapped.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# C.1.1 requirements.txt installable
# ---------------------------------------------------------------------------
def test_C_1_1_requirements_listing(project_root: Path) -> None:
    """C.1.1 — requirements.txt declares the core ABM stack."""
    req_file = project_root / "requirements.txt"
    assert req_file.is_file(), "requirements.txt must exist"

    content = req_file.read_text(encoding="utf-8").lower()
    required_packages = {"mesa", "numpy", "matplotlib", "hypothesis", "pytest"}
    missing = {pkg for pkg in required_packages if pkg not in content}
    assert not missing, f"requirements.txt missing packages: {missing}"


# ---------------------------------------------------------------------------
# C.1.2 README.md has run instructions
# ---------------------------------------------------------------------------
def test_C_1_2_readme_run_instructions(project_root: Path) -> None:
    """C.1.2 — README mentions the canonical run command + baseline config."""
    readme = project_root / "README.md"
    assert readme.is_file(), "README.md must exist"

    text = readme.read_text(encoding="utf-8")
    assert "python -m src.model" in text or "python -m simulations" in text, (
        "README must document the canonical run command"
    )
    assert "configs/baseline.yaml" in text, "README must reference baseline config"


# ---------------------------------------------------------------------------
# C.1.3 baseline.yaml parses + required fields
# ---------------------------------------------------------------------------
REQUIRED_BASELINE_FIELDS = {
    "seed",
    "n_genes",
    "n_developers",
    "n_seasons",
    "alpha",
    "decay_per_month",
    "decay_floor",
    "fitness_retention_rate",
    "newcomer_protection_days",
    "newcomer_bonus_multiplier",
    "developer_strategy_mix",
}


def test_C_1_3_baseline_config_schema(baseline_config_path: Path) -> None:
    """C.1.3 — baseline.yaml exists, parses, and carries every required field."""
    assert baseline_config_path.is_file(), "configs/baseline.yaml must exist"

    with baseline_config_path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    assert isinstance(cfg, dict), "baseline.yaml must parse as a mapping"
    missing = REQUIRED_BASELINE_FIELDS - set(cfg)
    assert not missing, f"baseline.yaml missing required fields: {missing}"


# ---------------------------------------------------------------------------
# C.1.4 Apache 2.0 LICENSE file
# ---------------------------------------------------------------------------
def test_C_1_4_license_apache_2(project_root: Path) -> None:
    """C.1.4 — Apache 2.0 LICENSE file present (plan §3.4 deliverable 2)."""
    license_file = project_root / "LICENSE"
    assert license_file.is_file(), "LICENSE file must exist"

    text = license_file.read_text(encoding="utf-8")
    assert "Apache License" in text, "LICENSE must be Apache License"
    assert "Version 2.0" in text, "LICENSE must be version 2.0"

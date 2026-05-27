"""Shared pytest fixtures for ABM simulation tests.

TDD scaffold — most fixtures intentionally minimal until stage 2.
"""

from __future__ import annotations

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project_root() -> Path:
    """Absolute path to the `simulations/` directory."""
    return PROJECT_ROOT


@pytest.fixture
def baseline_config_path(project_root: Path) -> Path:
    return project_root / "configs" / "baseline.yaml"


@pytest.fixture
def sweep_q2_config_path(project_root: Path) -> Path:
    return project_root / "configs" / "sweep_q2.yaml"


@pytest.fixture
def sweep_q3_config_path(project_root: Path) -> Path:
    return project_root / "configs" / "sweep_q3.yaml"


@pytest.fixture
def deterministic_seed() -> int:
    """Standard seed used by all deterministic tests."""
    return 42

"""C.9 — Q1–Q4 simulation problem readiness tests.

These tests verify that sweep configurations + reporting hooks exist.
Actual simulation runs are stage 2–3 work.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml


# ---------------------------------------------------------------------------
# C.9.1 — Q2 sweep alpha values loadable
# ---------------------------------------------------------------------------
def test_C_9_1_q2_alpha_values_loadable(sweep_q2_config_path: Path) -> None:
    """C.9.1 — sweep_q2.yaml lists the 5 canonical α values."""
    with sweep_q2_config_path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    sweep = cfg.get("sweep", {})
    assert sweep.get("parameter") == "alpha"
    assert sorted(sweep.get("values", [])) == [0.1, 0.3, 0.5, 0.7, 0.9]


# ---------------------------------------------------------------------------
# C.9.2 — Q3 sweep season-length values loadable
# ---------------------------------------------------------------------------
def test_C_9_2_q3_season_length_values_loadable(sweep_q3_config_path: Path) -> None:
    """C.9.2 — sweep_q3.yaml lists the 5 canonical season-length values."""
    with sweep_q3_config_path.open(encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    sweep = cfg.get("sweep", {})
    assert sweep.get("parameter") == "season_length_days"
    assert sorted(sweep.get("values", [])) == [30, 60, 90, 120, 180]


# ---------------------------------------------------------------------------
# C.9.3 — Q2 report scaffold contains HHI + α table
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_C_9_3_q2_report_contains_hhi_and_alpha_table(project_root: Path) -> None:
    """C.9.3 — Q2 notebook (or rendered report) carries an HHI plot + α table."""
    candidates = [
        project_root / "notebooks" / "q2_diversity_factor.ipynb",
        project_root / "reports" / "q2_diversity" / "report.md",
    ]
    if not any(p.exists() for p in candidates):
        pytest.xfail("Q2 notebook / report not yet generated — stage 2 produces it")

    text = next(p for p in candidates if p.exists()).read_text(encoding="utf-8")
    assert "HHI" in text
    assert "alpha" in text.lower() or "α" in text


# ---------------------------------------------------------------------------
# C.9.4 — Q3 report scaffold contains newcomer entry rate line chart
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_C_9_4_q3_report_contains_newcomer_rate_chart(project_root: Path) -> None:
    """C.9.4 — Q3 notebook (or rendered report) carries a newcomer-rate chart."""
    candidates = [
        project_root / "notebooks" / "q3_season_length.ipynb",
        project_root / "reports" / "q3_season_length" / "report.md",
    ]
    if not any(p.exists() for p in candidates):
        pytest.xfail("Q3 notebook / report not yet generated — stage 2 produces it")

    text = next(p for p in candidates if p.exists()).read_text(encoding="utf-8")
    assert "newcomer" in text.lower()

"""C.10 — Sweep runner tests (Stage-3 R8).

Covers ``execute_sweep`` smoke path + ``aggregate`` statistical helper +
``override_config`` parameter routing.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# C.10.1 — override_config rejects unknown parameter
# ---------------------------------------------------------------------------
def test_C_10_1_override_config_unknown_parameter(baseline_config_path: Path) -> None:
    """C.10.1 — typos in sweep YAML must fail loudly, not silently fall back."""
    from src.model import load_config
    from src.sweep_runner import override_config

    config = load_config(baseline_config_path)
    with pytest.raises(ValueError, match="no matching ModelConfig field"):
        override_config(config, "alphax", 0.5)


def test_C_10_1_override_config_replaces_alpha(baseline_config_path: Path) -> None:
    """C.10.1 — alpha override produces a ModelConfig clone with new alpha."""
    from src.model import load_config
    from src.sweep_runner import override_config

    config = load_config(baseline_config_path)
    new_config = override_config(config, "alpha", 0.7)
    assert new_config.alpha == 0.7
    assert config.alpha == 0.5  # original untouched


def test_C_10_1_override_config_season_length_days_syncs_steps(
    baseline_config_path: Path,
) -> None:
    """C.10.1 — Stage-3 R9: season_length_days override re-derives n_steps_per_season."""
    from src.model import DAYS_PER_STEP, load_config
    from src.sweep_runner import override_config

    config = load_config(baseline_config_path)
    for days in (30, 60, 90, 120, 180):
        new_config = override_config(config, "season_length_days", days)
        expected_steps = max(1, round(days / DAYS_PER_STEP))
        assert new_config.season_length_days == days
        assert new_config.n_steps_per_season == expected_steps, (
            f"season_length_days={days} should yield n_steps_per_season={expected_steps}, "
            f"got {new_config.n_steps_per_season}"
        )
    assert config.n_steps_per_season == 30  # original untouched


# ---------------------------------------------------------------------------
# C.10.2 — aggregate computes mean / std / ci95 correctly
# ---------------------------------------------------------------------------
def test_C_10_2_aggregate_basic_stats() -> None:
    """C.10.2 — known-input aggregate matches hand-computed mean/std/ci95."""
    from src.sweep_runner import aggregate

    rows = [
        {"HHI": 100.0, "alpha": 0.5},
        {"HHI": 200.0, "alpha": 0.5},
        {"HHI": 300.0, "alpha": 0.5},
        {"HHI": 400.0, "alpha": 0.5},
        {"HHI": 500.0, "alpha": 0.5},
    ]
    summary = aggregate(rows, ["HHI"])
    assert "HHI" in summary
    assert summary["HHI"]["n"] == 5.0
    assert summary["HHI"]["mean"] == pytest.approx(300.0)
    assert summary["HHI"]["std"] == pytest.approx(158.113883, rel=1e-5)
    assert summary["HHI"]["ci95"] == pytest.approx(138.592929, rel=1e-5)


def test_C_10_2_aggregate_empty() -> None:
    """C.10.2 — empty rows ⇒ empty aggregate, no exception."""
    from src.sweep_runner import aggregate

    assert aggregate([], ["HHI"]) == {}


def test_C_10_2_aggregate_single_row_zero_variance() -> None:
    """C.10.2 — single-row metric ⇒ std=0, ci95=0 (graceful, not div-by-zero)."""
    from src.sweep_runner import aggregate

    summary = aggregate([{"HHI": 42.0}], ["HHI"])
    assert summary["HHI"]["mean"] == pytest.approx(42.0)
    assert summary["HHI"]["std"] == 0.0
    assert summary["HHI"]["ci95"] == 0.0


# ---------------------------------------------------------------------------
# C.10.3 — execute_sweep dry-run smoke (1 run per value, no output write)
# ---------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.slow
def test_C_10_3_execute_sweep_dry_run_q2(
    sweep_q2_config_path: Path,
    tmp_path: Path,
) -> None:
    """C.10.3 — Q2 dry-run produces 5 rows (1 per α) with required keys."""
    from src.sweep_runner import execute_sweep

    manifest = execute_sweep(
        sweep_q2_config_path,
        dry_run=True,
        write_outputs=False,
    )

    assert manifest["parameter"] == "alpha"
    assert sorted(manifest["values"]) == [0.1, 0.3, 0.5, 0.7, 0.9]
    assert manifest["n_runs_per_param"] == 1
    assert len(manifest["rows"]) == 5

    for row in manifest["rows"]:
        assert "alpha" in row
        assert "run_idx" in row
        assert "seed" in row
        for metric in ("HHI", "shannon_diversity", "top10_share"):
            assert metric in row, (
                f"row missing metric {metric!r}: {row}"
            )

    seeds = [row["seed"] for row in manifest["rows"]]
    assert len(set(seeds)) == len(seeds), "seeds must be unique per (value, run_idx)"

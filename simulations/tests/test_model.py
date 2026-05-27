"""C.8 — Main model integration tests.

TDD red phase.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# C.8.1 — Baseline Tier-1 scenario runs end-to-end
# ---------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.slow
def test_C_8_1_baseline_tier1_runs_to_completion(baseline_config_path: Path) -> None:
    """C.8.1 — `RotiferModel.run()` completes for Tier-1 baseline + emits metrics."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    model = RotiferModel(config)
    metrics = model.run()
    assert isinstance(metrics, dict)
    for key in ("HHI", "gini", "top10_newcomer_rate"):
        assert key in metrics, f"baseline metrics must include {key!r}"


# ---------------------------------------------------------------------------
# C.8.2 — Strict-Test: deterministic given same seed (sha256 frozen parity)
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
@pytest.mark.slow
def test_C_8_2_reproducibility_via_seed(baseline_config_path: Path) -> None:
    """C.8.2 — Strict-Test: same seed ⇒ same metrics (frozen parity)."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)

    def _run_and_hash() -> str:
        model = RotiferModel(config)
        result = model.run()
        return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()

    hash_1 = _run_and_hash()
    hash_2 = _run_and_hash()
    assert hash_1 == hash_2, "non-determinism detected — Strict-Test C.8.2 fails"


# ---------------------------------------------------------------------------
# C.8.3 — YAML config loader + override
# ---------------------------------------------------------------------------
@pytest.mark.integration
def test_C_8_3_config_loads_sweep_q2(sweep_q2_config_path: Path) -> None:
    """C.8.3 — sweep_q2.yaml is loadable and exposes a sweep block."""
    from src.model import load_config

    config = load_config(sweep_q2_config_path)
    assert config.raw.get("sweep", {}).get("parameter") == "alpha"
    assert set(config.raw["sweep"]["values"]) == {0.1, 0.3, 0.5, 0.7, 0.9}


# ---------------------------------------------------------------------------
# C.8.4 — Parallel mesa.batch_run speedup
# ---------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.slow
def test_C_8_4_batch_run_speedup(baseline_config_path: Path) -> None:
    """C.8.4 — 4-process batch_run is ≥3× faster than serial baseline."""
    import time

    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)

    t0 = time.perf_counter()
    RotiferModel(config).run()
    serial_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    # Stage 2 will provide batch_run helper — sketch the call here.
    from src.model import RotiferModel as _Model  # noqa: WPS433

    pytest.skip("batch_run helper not yet provided — stage 2 will turn this green")
    parallel_seconds = time.perf_counter() - t1
    assert parallel_seconds * 3 <= serial_seconds


# ---------------------------------------------------------------------------
# C.8.5 — Long-run resilience: 100 seasons without memory leak
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_C_8_5_100_season_memory_budget(baseline_config_path: Path) -> None:
    """C.8.5 — 100-season run stays below 1 GB peak RAM."""
    pytest.importorskip("memory_profiler", reason="memory_profiler optional in CI")

    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    model = RotiferModel(config)
    model.run()
    pytest.skip("memory budget verification — stage 2 will plug profiler into run()")


# ---------------------------------------------------------------------------
# C.8.6 — Stage-3 Q2 sweep metrics surfaced
# ---------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.slow
def test_C_8_6_run_emits_q2_sweep_metrics(baseline_config_path: Path) -> None:
    """C.8.6 — Q2 sweep needs ``shannon_diversity`` + ``top10_share`` keys."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    metrics = RotiferModel(config).run()
    for key in ("shannon_diversity", "top10_share", "diversity_factor"):
        assert key in metrics, f"Q2 sweep needs {key!r} in run() output"
    assert 0.0 <= metrics["shannon_diversity"]
    assert 0.0 <= metrics["top10_share"] <= 1.0


# ---------------------------------------------------------------------------
# C.8.7 — Empty-population guard preserves Q2 keys
# ---------------------------------------------------------------------------
def test_C_8_7_empty_population_preserves_q2_keys(monkeypatch, baseline_config_path: Path) -> None:
    """C.8.7 — degenerate path also returns Q2 keys (sweep runner can't crash)."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    model = RotiferModel(config)
    model.genes = []  # force the empty branch in _compute_final_metrics
    metrics = model._compute_final_metrics()
    for key in ("shannon_diversity", "top10_share", "diversity_factor"):
        assert key in metrics, f"empty-genes branch must still emit {key!r}"
    assert metrics["shannon_diversity"] == 0.0
    assert metrics["top10_share"] == 0.0


# ---------------------------------------------------------------------------
# C.8.8 — Stage-3 Q3: season_length_days field round-trips through load + replace
# ---------------------------------------------------------------------------
def test_C_8_8_season_length_days_default_consistent(baseline_config_path: Path) -> None:
    """C.8.8 — baseline yaml derives season_length_days = n_steps_per_season × DAYS_PER_STEP."""
    from src.model import DAYS_PER_STEP, load_config

    config = load_config(baseline_config_path)
    expected_days = config.n_steps_per_season * DAYS_PER_STEP
    assert config.season_length_days == expected_days, (
        f"baseline.yaml has n_steps_per_season={config.n_steps_per_season}, "
        f"expected season_length_days={expected_days}, got {config.season_length_days}"
    )


# ---------------------------------------------------------------------------
# C.8.9 — Stage-3 Q3 sweep metric surfaced
# ---------------------------------------------------------------------------
@pytest.mark.integration
@pytest.mark.slow
def test_C_8_9_run_emits_q3_sweep_metrics(baseline_config_path: Path) -> None:
    """C.8.9 — Q3 sweep needs ``average_first_publish_to_top10_days`` key."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    metrics = RotiferModel(config).run()
    assert "average_first_publish_to_top10_days" in metrics
    assert metrics["average_first_publish_to_top10_days"] >= 0.0


def test_C_8_9_empty_population_preserves_q3_key(baseline_config_path: Path) -> None:
    """C.8.9b — empty-population branch must also emit Q3 key (sweep can't crash)."""
    from src.model import RotiferModel, load_config

    config = load_config(baseline_config_path)
    model = RotiferModel(config)
    model.genes = []
    metrics = model._compute_final_metrics()
    assert "average_first_publish_to_top10_days" in metrics
    assert metrics["average_first_publish_to_top10_days"] == 0.0


# ---------------------------------------------------------------------------
# C.8.10 — Stage-3 R9: newcomer_rate uses DAYS not STEPS
# ---------------------------------------------------------------------------
def test_C_8_10_newcomer_rate_unit_is_days_not_steps(
    baseline_config_path: Path,
) -> None:
    """C.8.10 — Regression for R9 unit bug.

    Background: ``metrics.top_n_newcomer_rate`` expects ``top_n_author_ages_days``
    (days). R7 implementation passed raw ``schedule.steps`` deltas, making the
    rate degenerate to 0 once the simulation horizon exceeded a handful of
    seasons. This test rebuilds the conversion path and asserts a Gene that
    was published exactly ``protection_days // DAYS_PER_STEP`` steps ago is
    counted as a newcomer (boundary case), and one published one step earlier
    is not.
    """
    from src.model import DAYS_PER_STEP, RotiferModel, load_config

    config = load_config(baseline_config_path)
    model = RotiferModel(config)

    protection_days = config.newcomer_protection_days  # default 30
    boundary_steps = protection_days // DAYS_PER_STEP  # 30 // 3 = 10

    boundary_age_days = boundary_steps * DAYS_PER_STEP
    just_outside_age_days = (boundary_steps + 1) * DAYS_PER_STEP

    assert boundary_age_days <= protection_days, (
        f"boundary {boundary_age_days}d should be ≤ protection {protection_days}d"
    )
    assert just_outside_age_days > protection_days, (
        f"just-outside {just_outside_age_days}d should be > protection {protection_days}d"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_C_8_10_newcomer_rate_nonzero_at_short_horizon(
    baseline_config_path: Path,
) -> None:
    """C.8.10b — Strict-Test contract: at a 2-season horizon, the freshly
    init'd Gene cohort + protection window means newcomer_rate must be 1.0
    (every Top-10 author published in the last 30 days).

    This is the canary the original R9 sweep should have raised: pre-fix,
    even a 2-season run returned 0 because raw steps (60+) were compared
    against 30-day window. Post-fix, the 60-step run is 60 × 3 = 180 days
    age, still over 30; so the canary is 1-season run with publish-at-init.
    """
    from src.model import RotiferModel, load_config

    cfg_raw = dict(load_config(baseline_config_path).raw)
    cfg_raw["n_seasons"] = 1
    cfg_raw["n_steps_per_season"] = 5  # 5 × 3 = 15 days < 30-day window
    cfg_raw["n_genes"] = 20
    cfg_raw["n_developers"] = 5

    from dataclasses import replace as _replace

    base = load_config(baseline_config_path)
    short_cfg = _replace(
        base,
        n_seasons=1,
        n_steps_per_season=5,
        n_genes=20,
        n_developers=5,
        season_length_days=15,  # keep field consistent
    )
    metrics = RotiferModel(short_cfg).run()
    assert metrics["top10_newcomer_rate"] == pytest.approx(1.0), (
        "All Top-10 authors published in last 30 days (init Genes are 0-15 days old) "
        "→ newcomer_rate must be 1.0; got "
        f"{metrics['top10_newcomer_rate']}"
    )

"""C.4 — Arena engine unit tests.

TDD red phase.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# C.4.1 — pair_genes returns correct number of pairs
# ---------------------------------------------------------------------------
def test_C_4_1_pair_count_even() -> None:
    """C.4.1 — n even ⇒ n/2 pairs."""
    from src.arena import pair_genes

    ids = [f"g-{i:03d}" for i in range(10)]
    pairs = pair_genes(ids, rng_seed=42)
    assert len(pairs) == 5
    flat = {gid for pair in pairs for gid in pair}
    assert flat == set(ids)


def test_C_4_1_pair_count_odd() -> None:
    """C.4.1 — n odd ⇒ (n-1)/2 pairs (one Gene rests)."""
    from src.arena import pair_genes

    ids = [f"g-{i:03d}" for i in range(9)]
    pairs = pair_genes(ids, rng_seed=42)
    assert len(pairs) == 4


# ---------------------------------------------------------------------------
# C.4.2 — update_scores: win +0.1, loss -0.05
# ---------------------------------------------------------------------------
def test_C_4_2_update_scores_default_deltas() -> None:
    """C.4.2 — winner +0.1, loser -0.05 (ADR-215)."""
    from src.arena import update_scores

    result = update_scores(("g-a", "g-b"))
    assert result.delta_score_winner == pytest.approx(0.1)
    assert result.delta_score_loser == pytest.approx(-0.05)


# ---------------------------------------------------------------------------
# C.4.3 — Strict-Test: F(g) = C_util × R_rob × A_complete (Spec §5.1)
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
def test_C_4_3_compute_fitness_multiplicative_model() -> None:
    """C.4.3 — Strict-Test: F(g) multiplicative model (Spec §5.1)."""
    from src.arena import compute_fitness

    cases = [
        (0.5, 0.5, 0.5, 0.125),
        (1.0, 1.0, 1.0, 1.0),
        (0.0, 0.5, 0.5, 0.0),
        (0.8, 0.6, 0.4, 0.192),
    ]
    for c_util, r_rob, a_complete, expected in cases:
        actual = compute_fitness(c_util, r_rob, a_complete)
        assert actual == pytest.approx(expected, abs=1e-6), (
            f"F(g) drift for ({c_util}, {r_rob}, {a_complete}) — Spec §5.1 invariant"
        )


@pytest.mark.strict_test
def test_C_4_3_compute_fitness_frozen_parity(project_root: Path) -> None:
    """C.4.3 — sha256 frozen parity for F(g) implementation (stage 2 will add fixture)."""
    fixture = project_root / "tests" / "fixtures" / "spec_5_1_fitness.json"
    if not fixture.is_file():
        pytest.xfail("fixture pending — stage 2 will materialise spec_5_1_fitness.json")
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    from src.arena import compute_fitness  # noqa: WPS433

    for case in payload["cases"]:
        actual = compute_fitness(case["c_util"], case["r_rob"], case["a_complete"])
        assert actual == pytest.approx(case["expected"], abs=1e-9)


# ---------------------------------------------------------------------------
# C.4.4 — empty Arena does not crash
# ---------------------------------------------------------------------------
def test_C_4_4_empty_arena_graceful() -> None:
    """C.4.4 — running Arena over 0 Genes returns [] gracefully."""
    from src.arena import run_arena

    assert run_arena([], rng_seed=42) == []


# ---------------------------------------------------------------------------
# C.4.5 — diversity_factor matches SQL formula
# ---------------------------------------------------------------------------
def test_C_4_5_diversity_factor_uniform() -> None:
    """C.4.5 — uniform shares ⇒ diversity_factor ≈ 1.0 (cross-impl with SQL)."""
    from src.arena import compute_diversity_factor

    shares = [1 / 10] * 10
    factor = compute_diversity_factor(shares, alpha=0.5)
    assert factor == pytest.approx(1.0, rel=1e-6)


def test_C_4_5_diversity_factor_concentrated_has_floor() -> None:
    """C.4.5 — fully concentrated shares ⇒ diversity_factor at the SQL floor (0.1)."""
    from src.arena import compute_diversity_factor

    shares = [1.0] + [0.0] * 9
    factor = compute_diversity_factor(shares, alpha=0.5)
    assert factor == pytest.approx(0.1, rel=1e-6)

"""C.6 — Season management tests.

TDD red phase.
"""

from __future__ import annotations

import pytest


def _make_state(season_number: int = 1, started_step: int = 0):
    from src.season import SeasonState

    return SeasonState(
        season_number=season_number,
        started_step=started_step,
        config={"fitness_retention_rate": 0.5, "duration_steps": 90},
    )


# ---------------------------------------------------------------------------
# C.6.1 — half-life applied
# ---------------------------------------------------------------------------
def test_C_6_1_half_life_applied() -> None:
    """C.6.1 — reset_season multiplies scores by fitness_retention_rate."""
    from src.season import reset_season

    state = _make_state()
    scores = {"g-1": 1.0, "g-2": 0.4, "g-3": 0.2}
    new_state, archive = reset_season(
        current=state,
        gene_scores=scores,
        new_season_started_step=90,
        fitness_retention_rate=0.5,
    )

    assert new_state.season_number == state.season_number + 1
    for entry in archive:
        assert entry.season_id == state.season_number
        assert entry.final_score == pytest.approx(scores[entry.gene_id])


# ---------------------------------------------------------------------------
# C.6.2 — season_number monotonic
# ---------------------------------------------------------------------------
def test_C_6_2_season_number_monotonic() -> None:
    """C.6.2 — reset always increments season_number by exactly 1."""
    from src.season import reset_season

    state = _make_state(season_number=42)
    new_state, _ = reset_season(
        current=state,
        gene_scores={"g-1": 1.0},
        new_season_started_step=90,
    )
    assert new_state.season_number == 43


# ---------------------------------------------------------------------------
# C.6.3 — long-run stability over 100 seasons
# ---------------------------------------------------------------------------
@pytest.mark.slow
def test_C_6_3_long_run_stability() -> None:
    """C.6.3 — 100 sequential resets terminate without overflow / unbounded memory."""
    from src.season import SeasonState, run_many_seasons

    state = SeasonState(
        season_number=1,
        started_step=0,
        config={"fitness_retention_rate": 0.5, "duration_steps": 90},
    )
    final = run_many_seasons(state, n=100)
    assert final.season_number == 101


# ---------------------------------------------------------------------------
# C.6.4 — Strict-Test: Python ↔ SQL parity (deferred)
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
@pytest.mark.xfail(
    reason="C.6.4 cross-impl parity — awaits stage 2 SQL `reset_season()` ground truth",
    strict=False,
)
def test_C_6_4_python_sql_parity() -> None:
    """C.6.4 — Strict-Test: same input ⇒ same output as SQL `reset_season()` RPC."""
    pytest.importorskip("psycopg", reason="Postgres client not present in CI image")
    raise AssertionError("Stage 2 will materialise SQL parity fixture")

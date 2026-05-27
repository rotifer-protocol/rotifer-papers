"""C.5 — Reputation tests (Python mirror of Cloud SQL).

TDD red phase.
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# C.5.1 — Strict-Test: formula parity with Cloud SQL
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
def test_C_5_1_reputation_default_weights() -> None:
    """C.5.1 — Strict-Test: R = 0.5×fitness + 0.3×consistency + 0.2×endorsement."""
    from src.reputation import compute

    r = compute(fitness=1.0, consistency=1.0, endorsement=1.0)
    assert r == pytest.approx(1.0, abs=1e-9)

    r2 = compute(fitness=0.4, consistency=0.6, endorsement=0.2)
    expected = 0.5 * 0.4 + 0.3 * 0.6 + 0.2 * 0.2
    assert r2 == pytest.approx(expected, abs=1e-9)


# ---------------------------------------------------------------------------
# C.5.2 — Decay 0.05 per inactive month
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("months,expected", [(0, 0.50), (1, 0.45), (2, 0.40), (3, 0.35)])
def test_C_5_2_monthly_decay(months: int, expected: float) -> None:
    """C.5.2 — 0.05/month decay tested at months 0/1/2/3."""
    from src.reputation import apply_decay

    r = apply_decay(reputation=0.5, months_inactive=months, decay_floor=0.0)
    assert r == pytest.approx(expected, abs=1e-9)


# ---------------------------------------------------------------------------
# C.5.3 — Decay floor parameter respected
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("floor", [0.01, 0.05, 0.10, 0.20])
def test_C_5_3_decay_floor(floor: float) -> None:
    """C.5.3 — long-inactive reputation never falls below decay_floor."""
    from src.reputation import apply_decay

    r = apply_decay(reputation=0.5, months_inactive=10_000, decay_floor=floor)
    assert r == pytest.approx(floor, abs=1e-9)


# ---------------------------------------------------------------------------
# C.5.4 — Property: result is always in [0, 1]
# ---------------------------------------------------------------------------
@pytest.mark.property
def test_C_5_4_reputation_within_unit_interval() -> None:
    """C.5.4 — property: reputation ∈ [0, 1] for any reasonable input."""
    from hypothesis import given, strategies as st

    from src.reputation import compute

    @given(
        fitness=st.floats(min_value=0, max_value=1),
        consistency=st.floats(min_value=0, max_value=1),
        endorsement=st.floats(min_value=0, max_value=1),
    )
    def _prop(fitness: float, consistency: float, endorsement: float) -> None:
        r = compute(
            fitness=fitness,
            consistency=consistency,
            endorsement=endorsement,
        )
        assert 0.0 <= r <= 1.0

    _prop()


# ---------------------------------------------------------------------------
# C.5.5 — Strict-Test: Python ↔ Rust ↔ SQL parity (deferred to stage 2)
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
@pytest.mark.xfail(reason="C.5.5 cross-impl parity — awaits stage 2 Rust + SQL impls", strict=False)
def test_C_5_5_python_rust_sql_parity() -> None:
    """C.5.5 — Strict-Test: Python `compute` ≡ Rust `compute_reputation` ≡ SQL RPC.

    Marked xfail until both Rust and SQL implementations land in stage 2.
    """
    from src.reputation import compute

    rust_outputs = pytest.importorskip(
        "rotifer_core",
        reason="Rust compute_reputation not yet exposed via napi",
    )
    sql_outputs = pytest.importorskip(
        "psycopg",
        reason="SQL compute_all_reputations cannot be invoked without DB",
    )
    py = compute(fitness=0.5, consistency=0.5, endorsement=0.5)
    assert py == rust_outputs.compute_reputation(0.5, 0.5, 0.5)
    assert py == sql_outputs.compute_all_reputations(0.5, 0.5, 0.5)

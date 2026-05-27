"""C.5.4 supplementary property tests — reputation invariants."""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st


@pytest.mark.property
def test_reputation_clamped_to_unit_interval_property() -> None:
    """C.5.4 (property) — reputation ∈ [0, 1] for any reasonable input."""
    from src.reputation import compute

    @given(
        fitness=st.floats(min_value=0, max_value=1),
        consistency=st.floats(min_value=0, max_value=1),
        endorsement=st.floats(min_value=0, max_value=1),
    )
    def _prop(fitness: float, consistency: float, endorsement: float) -> None:
        r = compute(fitness=fitness, consistency=consistency, endorsement=endorsement)
        assert 0.0 <= r <= 1.0

    _prop()


@pytest.mark.property
def test_decay_floor_never_violated_property() -> None:
    """C.5.3 (property) — decay output always ≥ floor."""
    from src.reputation import apply_decay

    @given(
        initial=st.floats(min_value=0.0, max_value=1.0),
        months=st.integers(min_value=0, max_value=1_000),
        floor=st.floats(min_value=0.0, max_value=0.5),
    )
    def _prop(initial: float, months: int, floor: float) -> None:
        r = apply_decay(reputation=initial, months_inactive=months, decay_floor=floor)
        assert r >= floor - 1e-9

    _prop()

"""C.3.2 / C.3.4 supplementary property tests for Gene Agent invariants."""

from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

import mesa


@pytest.mark.property
def test_publish_fitness_in_unit_interval_property() -> None:
    """C.3.2 (property) — base_fitness ∈ [0, 1] ⇒ Gene fitness ∈ [0, 1]."""

    @given(base=st.floats(min_value=0, max_value=1))
    def _prop(base: float) -> None:
        from src.agents.developer_agent import DeveloperAgent, Strategy

        model = mesa.Model()
        dev = DeveloperAgent(
            unique_id=1,
            model=model,
            developer_id="dev",
            strategy=Strategy.INSTALL,
        )
        gene = dev.publish_gene(domain="d", base_fitness=base)
        assert 0.0 <= gene.fitness <= 1.0

    _prop()


@pytest.mark.property
def test_carr_fitness_in_70_130_percent_range_property() -> None:
    """C.3.4 (property) — Carr publish fitness ∈ [base × 0.7, base × 1.3]."""

    @given(base=st.floats(min_value=0.1, max_value=0.9))
    def _prop(base: float) -> None:
        from src.agents.developer_agent import DeveloperAgent, Strategy

        model = mesa.Model()
        dev = DeveloperAgent(
            unique_id=1,
            model=model,
            developer_id="dev",
            strategy=Strategy.CARR,
        )
        gene = dev.publish_gene(domain="d", base_fitness=base)
        assert base * 0.7 <= gene.fitness <= base * 1.3

    _prop()

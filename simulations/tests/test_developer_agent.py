"""C.3 — Developer Agent unit tests.

TDD red phase.
"""

from __future__ import annotations

import pytest
import mesa


def _make_dev(model: mesa.Model = None, **overrides):
    from src.agents.developer_agent import DeveloperAgent, Strategy

    if model is None:
        model = mesa.Model()
    defaults = {
        "developer_id": "dev-001",
        "strategy": Strategy.INSTALL,
    }
    defaults.update(overrides)
    return DeveloperAgent(unique_id=1, model=model, **defaults)


# ---------------------------------------------------------------------------
# C.3.1 — Strategy enum
# ---------------------------------------------------------------------------
def test_C_3_1_strategy_enum_values() -> None:
    """C.3.1 — Strategy enum exposes install + carr."""
    from src.agents.developer_agent import Strategy

    assert Strategy.INSTALL.value == "install"
    assert Strategy.CARR.value == "carr"
    assert {s.value for s in Strategy} == {"install", "carr"}


# ---------------------------------------------------------------------------
# C.3.2 — Property: publish initialises fitness in a uniform-ish range
# ---------------------------------------------------------------------------
def test_C_3_2_publish_fitness_within_unit_interval() -> None:
    """C.3.2 — A freshly published Gene has fitness in [0, 1]."""
    dev = _make_dev()
    gene = dev.publish_gene(domain="math.sort", base_fitness=0.5)
    assert 0.0 <= gene.fitness <= 1.0


# ---------------------------------------------------------------------------
# C.3.3 — Carr strategy costs 3× install
# ---------------------------------------------------------------------------
def test_C_3_3_carr_cost_is_three_times_install() -> None:
    """C.3.3 — Carr strategy publish cost == 3× install cost (Q2.5 design)."""
    from src.agents.developer_agent import Strategy

    install = _make_dev(strategy=Strategy.INSTALL)
    carr = _make_dev(developer_id="dev-002", strategy=Strategy.CARR)

    g1 = install.publish_gene(domain="d", base_fitness=0.5)
    g2 = carr.publish_gene(domain="d", base_fitness=0.5)

    assert g2.state.metadata["publish_cost"] == pytest.approx(
        3.0 * g1.state.metadata["publish_cost"]
    ), "carr cost must be exactly 3× install cost"


# ---------------------------------------------------------------------------
# C.3.4 — Carr fitness lies in [orig × 0.7, orig × 1.3]
# ---------------------------------------------------------------------------
def test_C_3_4_carr_fitness_range() -> None:
    """C.3.4 — Carr publish fitness ∈ [base × 0.7, base × 1.3]."""
    from src.agents.developer_agent import Strategy

    dev = _make_dev(strategy=Strategy.CARR)
    base = 0.5
    for _ in range(100):
        g = dev.publish_gene(domain="d", base_fitness=base)
        assert base * 0.7 <= g.fitness <= base * 1.3


# ---------------------------------------------------------------------------
# C.3.5 — Strict-Test: first_publish_step is monotonic
# ---------------------------------------------------------------------------
@pytest.mark.strict_test
def test_C_3_5_first_publish_step_monotonic() -> None:
    """C.3.5 — Strict-Test: first_publish_step must never regress (§35.3.2 MUST)."""
    dev = _make_dev()
    assert dev.first_publish_step is None

    dev.model.schedule.steps = 5  # simulated step counter
    dev.publish_gene(domain="d", base_fitness=0.5)
    first = dev.first_publish_step
    assert first == 5

    dev.model.schedule.steps = 12
    dev.publish_gene(domain="d", base_fitness=0.5)
    assert dev.first_publish_step == first, (
        "first_publish_step must remain the earliest publish step"
    )

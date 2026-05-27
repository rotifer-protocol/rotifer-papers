"""C.2 — Gene Agent unit tests.

TDD red phase: all behavioural assertions will fail until stage 2 ships impl.
"""

from __future__ import annotations

import pickle

import pytest

import mesa


def _make_gene(model: mesa.Model = None, **overrides):
    from src.agents.gene_agent import GeneAgent

    if model is None:
        model = mesa.Model()
    defaults = {
        "gene_id": "g-001",
        "domain": "math.sort",
        "fitness": 0.5,
        "created_step": 0,
        "author_id": "dev-001",
    }
    defaults.update(overrides)
    return GeneAgent(unique_id=1, model=model, **defaults)


# ---------------------------------------------------------------------------
# C.2.1 — required fields
# ---------------------------------------------------------------------------
def test_C_2_1_required_fields_present() -> None:
    """C.2.1 — GeneAgent exposes id / domain / fitness / created_step / author_id."""
    gene = _make_gene()
    assert gene.gene_id == "g-001"
    assert gene.domain == "math.sort"
    assert gene.fitness == pytest.approx(0.5)
    assert gene.created_step == 0
    assert gene.author_id == "dev-001"


# ---------------------------------------------------------------------------
# C.2.2 — step() updates fitness (growth on usage / decay otherwise)
# ---------------------------------------------------------------------------
def test_C_2_2_step_grows_fitness_with_usage() -> None:
    """C.2.2 — `step()` grows fitness after a usage signal."""
    gene = _make_gene(fitness=0.5)
    gene.state.metadata["usage_this_step"] = 1
    gene.step()
    assert gene.fitness > 0.5, "fitness must grow on usage"


def test_C_2_2_step_decays_fitness_without_usage() -> None:
    """C.2.2 — `step()` decays fitness by 0.05/month equivalent when idle."""
    gene = _make_gene(fitness=0.5)
    initial = gene.fitness
    for _ in range(30):
        gene.step()
    assert gene.fitness < initial, "idle gene fitness must decay"


# ---------------------------------------------------------------------------
# C.2.3 — retire condition (boundary)
# ---------------------------------------------------------------------------
def test_C_2_3_retire_threshold_exact_boundary() -> None:
    """C.2.3 — should_retire fires at exactly N consecutive below-threshold seasons."""
    gene = _make_gene(fitness=0.05)
    gene.state.consecutive_below_threshold_seasons = 3
    assert gene.should_retire(threshold=0.1, seasons_required=3) is True


def test_C_2_3_retire_threshold_one_below_required() -> None:
    """C.2.3 — N-1 seasons → not yet retired."""
    gene = _make_gene(fitness=0.05)
    gene.state.consecutive_below_threshold_seasons = 2
    assert gene.should_retire(threshold=0.1, seasons_required=3) is False


# ---------------------------------------------------------------------------
# C.2.4 — pickle round-trip
# ---------------------------------------------------------------------------
def test_C_2_4_pickle_roundtrip_preserves_state() -> None:
    """C.2.4 — pickle/unpickle preserves all visible state."""
    gene = _make_gene(fitness=0.42)
    blob = pickle.dumps(gene)
    restored = pickle.loads(blob)
    assert restored.gene_id == gene.gene_id
    assert restored.fitness == pytest.approx(gene.fitness)
    assert restored.domain == gene.domain
    assert restored.created_step == gene.created_step

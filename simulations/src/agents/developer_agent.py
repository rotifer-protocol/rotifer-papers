"""Developer Agent — publishes Genes with `install` or `carr` strategy.

Stage 2 R5: ``publish_gene`` + monotonic ``first_publish_step`` implemented.
``step()`` (probabilistic per-tick publication loop) deferred to R6 where
the Model layer integrates schedules.

Verified by:
    - tests/test_developer_agent.py (C.3.1–C.3.5)
    - tests/property/test_gene_properties.py (publish + carr range)
"""

from __future__ import annotations

import types
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import mesa

from .gene_agent import GeneAgent

INSTALL_COST = 1.0
CARR_COST_MULTIPLIER = 3.0  # ADR-260 C3 — Carr training is 3× baseline cost.

CARR_FITNESS_LOW = 0.7
CARR_FITNESS_HIGH = 1.3

FITNESS_MIN = 0.0
FITNESS_MAX = 1.0

GENE_UID_OFFSET = 1_000_000  # Per-developer offset to keep Gene unique_ids collision-free.

# R7 step() defaults — picked to match baseline.yaml scale (30 steps/season ⇒
# ~1 publish per dev per season). Tunable via subclass override if Q2.5 / Q2.6
# sweeps want different cadences.
DEFAULT_PUBLISH_PROBABILITY = 1.0 / 30.0
DEFAULT_PUBLISH_FITNESS_LOW = 0.3
DEFAULT_PUBLISH_FITNESS_HIGH = 0.7
NUM_DOMAINS = 5  # matches RotiferModel._init_genes domain palette.


class Strategy(str, Enum):
    """Developer publication strategy.

    - INSTALL : standard publish; fitness = clamp(base, [0, 1]); cost = 1.0.
    - CARR    : Carr training (ADR-260 C3) — fitness = base × U(0.7, 1.3); cost = 3.0.
    """

    INSTALL = "install"
    CARR = "carr"


@dataclass
class DeveloperAgentState:
    developer_id: str
    strategy: Strategy
    first_publish_step: Optional[int] = None
    published_count: int = 0


class DeveloperAgent(mesa.Agent):
    """Developer Agent — decides when and how to publish Genes."""

    def __init__(
        self,
        unique_id: int,
        model: "mesa.Model",
        *,
        developer_id: str,
        strategy: Strategy = Strategy.INSTALL,
    ) -> None:
        super().__init__(unique_id, model)
        self.state = DeveloperAgentState(
            developer_id=developer_id,
            strategy=strategy,
        )
        self._ensure_schedule_stub()

    @property
    def developer_id(self) -> str:
        return self.state.developer_id

    @property
    def strategy(self) -> Strategy:
        return self.state.strategy

    @property
    def first_publish_step(self) -> Optional[int]:
        """Monotonic — must never regress once set. Verified by C.3.5."""
        return self.state.first_publish_step

    @property
    def published_count(self) -> int:
        return self.state.published_count

    def step(self) -> Optional[GeneAgent]:
        """Per-tick probabilistic publication trigger.

        R7 implements the simplest viable trigger: a Bernoulli draw against
        ``DEFAULT_PUBLISH_PROBABILITY`` (≈ 1 publish per 30 steps), with
        fitness drawn uniformly from a "plausible new-Gene" range. The
        Model layer collects the returned Gene (or ``None``) and registers
        it for the next Arena round.

        Returns:
            The freshly published GeneAgent, or ``None`` if this tick
            did not fire the publish event.
        """
        if self.model.random.random() >= DEFAULT_PUBLISH_PROBABILITY:
            return None
        base_fitness = self.model.random.uniform(
            DEFAULT_PUBLISH_FITNESS_LOW,
            DEFAULT_PUBLISH_FITNESS_HIGH,
        )
        domain = f"d-{self.model.random.randint(0, NUM_DOMAINS - 1)}"
        return self.publish_gene(domain=domain, base_fitness=base_fitness)

    def publish_gene(
        self,
        *,
        domain: str,
        base_fitness: float,
    ) -> GeneAgent:
        """Publish a new Gene; cost + fitness vary by strategy.

        Strategy semantics:
            INSTALL : fitness = clamp(base_fitness, [0, 1]),  publish_cost = 1.0
            CARR    : fitness = base_fitness × U(0.7, 1.3),    publish_cost = 3.0

        ADR-260 C3 invariant: Carr fitness is bounded *relative to base*
        (`[base × 0.7, base × 1.3]`) but is **not** clamped to [0, 1] — for
        large base, ``base × 1.3`` may exceed 1, which is acceptable per spec
        (and why the property test caps base at 0.9). The Arena later clamps
        on usage updates via ``GeneAgent.step``.

        Side-effects:
            - First call records ``state.first_publish_step`` from
              ``model.schedule.steps`` (monotonic — never regresses on
              subsequent calls). Verified by C.3.5.
            - ``state.published_count`` increments by 1.

        Verified by C.3.2 / C.3.3 / C.3.4 / C.3.5 + property tests.
        """
        self._ensure_schedule_stub()
        current_step = self.model.schedule.steps

        if self.strategy is Strategy.CARR:
            multiplier = self.model.random.uniform(CARR_FITNESS_LOW, CARR_FITNESS_HIGH)
            fitness = base_fitness * multiplier
            cost = INSTALL_COST * CARR_COST_MULTIPLIER
        else:
            fitness = max(FITNESS_MIN, min(FITNESS_MAX, base_fitness))
            cost = INSTALL_COST

        if self.state.first_publish_step is None:
            self.state.first_publish_step = current_step
        self.state.published_count += 1

        gene_id = f"{self.developer_id}-g{self.state.published_count:04d}"
        gene = GeneAgent(
            unique_id=self._next_gene_unique_id(),
            model=self.model,
            gene_id=gene_id,
            domain=domain,
            fitness=fitness,
            created_step=current_step,
            author_id=self.developer_id,
        )
        gene.state.metadata["publish_cost"] = cost
        gene.state.metadata["publish_strategy"] = self.strategy.value
        return gene

    def _ensure_schedule_stub(self) -> None:
        """Mesa 2.4 sets ``model.schedule = None`` until a scheduler is wired up.

        ``publish_gene`` and the C.3.5 test both need ``model.schedule.steps``
        to record / set ``first_publish_step``. We install a lightweight
        ``SimpleNamespace(steps=0)`` only when no scheduler has been attached;
        the real ``RotiferModel`` (R6+) replaces this with a Mesa scheduler
        whose ``steps`` counter advances naturally.
        """
        if getattr(self.model, "schedule", None) is None:
            self.model.schedule = types.SimpleNamespace(steps=0)

    def _next_gene_unique_id(self) -> int:
        """Generate a collision-free Gene unique_id within this model.

        Uses ``developer.unique_id × GENE_UID_OFFSET + published_count``;
        safe as long as developer unique_ids stay below GENE_UID_OFFSET (1M)
        and per-developer publish counts stay below GENE_UID_OFFSET — both
        comfortably outside ABM sweep ranges (Q1–Q4 cap n_developers ≤ 100,
        publishes-per-developer ≤ ~few hundred per run).
        """
        return self.unique_id * GENE_UID_OFFSET + self.state.published_count

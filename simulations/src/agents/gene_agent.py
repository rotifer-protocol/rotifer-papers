"""Gene Agent — represents a single Gene flowing through Arena / Season cycles.

Stage 2 R1: step() + should_retire() + pickle round-trip implemented.
Verified by tests/test_gene_agent.py (C.2.1–C.2.4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import mesa

USAGE_GROWTH_PER_HIT = 0.01
DECAY_PER_IDLE_STEP = 0.001
FITNESS_MIN = 0.0
FITNESS_MAX = 1.0


@dataclass
class GeneAgentState:
    """Externally visible state — exposed for tests and serialization."""

    gene_id: str
    domain: str
    fitness: float
    created_step: int
    author_id: str
    lifecycle_state: str = "Published"
    last_used_step: Optional[int] = None
    consecutive_below_threshold_seasons: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class GeneAgent(mesa.Agent):
    """Gene Agent — `step()` advances usage / decay / fitness.

    Required attributes (verified by C.2.1):
        - gene_id : str
        - domain : str
        - fitness : float
        - created_step : int
        - author_id : str
    """

    def __init__(
        self,
        unique_id: int,
        model: "mesa.Model",
        *,
        gene_id: str,
        domain: str,
        fitness: float,
        created_step: int,
        author_id: str,
    ) -> None:
        super().__init__(unique_id, model)
        self.state = GeneAgentState(
            gene_id=gene_id,
            domain=domain,
            fitness=fitness,
            created_step=created_step,
            author_id=author_id,
        )

    @property
    def gene_id(self) -> str:
        return self.state.gene_id

    @property
    def domain(self) -> str:
        return self.state.domain

    @property
    def fitness(self) -> float:
        return self.state.fitness

    @property
    def created_step(self) -> int:
        return self.state.created_step

    @property
    def author_id(self) -> str:
        return self.state.author_id

    def step(self) -> None:
        """Advance one simulation step — handle usage growth + decay.

        Reads `state.metadata['usage_this_step']` (set by the Arena before
        scheduling) and pops it so the next step starts clean.

        Usage > 0 → fitness += USAGE_GROWTH_PER_HIT × usage (capped at 1.0)
        Usage == 0 → fitness -= DECAY_PER_IDLE_STEP (floored at 0.0)
        """
        usage = self.state.metadata.pop("usage_this_step", 0)
        if usage > 0:
            delta = USAGE_GROWTH_PER_HIT * usage
            self.state.fitness = min(FITNESS_MAX, self.state.fitness + delta)
        else:
            self.state.fitness = max(FITNESS_MIN, self.state.fitness - DECAY_PER_IDLE_STEP)

    def should_retire(self, threshold: float, seasons_required: int) -> bool:
        """Retire iff fitness has been below `threshold` for ≥ N consecutive seasons.

        Note:
            The counter `state.consecutive_below_threshold_seasons` is the
            authoritative source of truth — the Season layer increments it
            at end-of-season when `fitness < threshold`, and resets it to 0
            when fitness recovers. We additionally guard with `fitness <
            threshold` for the current step so a Gene that just spiked back
            up isn't retired on a stale counter.
        """
        return (
            self.state.fitness < threshold
            and self.state.consecutive_below_threshold_seasons >= seasons_required
        )

    def __getstate__(self) -> dict[str, Any]:
        """Pickle: serialize only the data needed to reconstruct the agent.

        The mesa.Model back-reference is intentionally dropped — pickling
        whole Mesa models is brittle (RNG state, schedule, datacollector
        all chain), and the ABM checkpoint path re-attaches agents to a
        fresh model on restore.
        """
        return {"unique_id": self.unique_id, "state": self.state}

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Unpickle: restore state without invoking `__init__`.

        The model back-reference is left unset — restore callers must
        re-attach via `gene.model = new_model` before stepping.
        """
        self.__dict__.update(state)

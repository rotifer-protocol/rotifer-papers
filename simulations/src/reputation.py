"""Reputation computation — mirrors Cloud SQL `compute_all_reputations()`.

TDD scaffold for C.5.1–C.5.5. Implementation deferred to stage 2.

**Cross-implementation invariant** (Strict-Test C.5.5):
    Same input → same output as Rust `compute_reputation` and SQL RPC.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_FITNESS_WEIGHT = 0.5
DEFAULT_CONSISTENCY_WEIGHT = 0.3
DEFAULT_ENDORSEMENT_WEIGHT = 0.2

DEFAULT_DECAY_PER_MONTH = 0.05
DEFAULT_DECAY_FLOOR = 0.01

REPUTATION_MIN = 0.0
REPUTATION_MAX = 1.0


@dataclass(frozen=True)
class ReputationWeights:
    """ADR-157 — α, β, γ parameter triple."""

    fitness: float = DEFAULT_FITNESS_WEIGHT
    consistency: float = DEFAULT_CONSISTENCY_WEIGHT
    endorsement: float = DEFAULT_ENDORSEMENT_WEIGHT

    def sum(self) -> float:
        return self.fitness + self.consistency + self.endorsement


def compute(
    *,
    fitness: float,
    consistency: float,
    endorsement: float,
    weights: ReputationWeights | None = None,
) -> float:
    """R(g) = α·fitness + β·consistency + γ·endorsement.

    Verified by C.5.1 (Strict-Test — mirrors SQL `compute_all_reputations`).
    Output is clamped to [REPUTATION_MIN, REPUTATION_MAX] (C.5.4 property).
    """
    w = weights if weights is not None else ReputationWeights()
    raw = w.fitness * fitness + w.consistency * consistency + w.endorsement * endorsement
    return max(REPUTATION_MIN, min(REPUTATION_MAX, raw))


def apply_decay(
    reputation: float,
    *,
    months_inactive: int,
    decay_per_month: float = DEFAULT_DECAY_PER_MONTH,
    decay_floor: float = DEFAULT_DECAY_FLOOR,
) -> float:
    """Apply linear monthly decay with a configurable floor.

    Verified by C.5.2 and C.5.3.

    Formula: `max(reputation - months_inactive * decay_per_month, decay_floor)`.

    Notes:
        - Linear decay (not exponential) — matches Cloud SQL impl and is easier
          to reason about for property tests (monotonic, finite-step floor).
        - `decay_floor=0.0` lets caller see the raw line (used in C.5.2 to
          inspect intermediate values 0.50 → 0.45 → 0.40 → 0.35).
        - Negative `months_inactive` would *grow* reputation — silently clamped
          to 0 to keep the function total without raising (consumers in the ABM
          control-loop never pass negative; tests only assert ≥ 0).
    """
    months = max(0, months_inactive)
    decayed = reputation - months * decay_per_month
    return max(decay_floor, decayed)

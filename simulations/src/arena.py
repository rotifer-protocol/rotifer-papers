"""Arena engine — pairs Genes, computes F(g), updates scores.

Stage 2 R3: all five primitives implemented (pair_genes / update_scores /
compute_fitness / compute_diversity_factor / run_arena).

Verified by tests/test_arena.py (C.4.1–C.4.5).
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Sequence

DEFAULT_WIN_DELTA = 0.1
DEFAULT_LOSS_DELTA = -0.05
DIVERSITY_FLOOR = 0.1


@dataclass(frozen=True)
class BattleResult:
    """Single Arena pairing outcome."""

    winner_id: str
    loser_id: str
    delta_score_winner: float
    delta_score_loser: float


def pair_genes(gene_ids: Sequence[str], *, rng_seed: int) -> list[tuple[str, str]]:
    """Pair Genes for Arena battle.

    For n even returns n/2 pairs covering all Genes.
    For n odd returns (n-1)/2 pairs — one Gene rests this round.

    The `rng_seed` controls shuffle determinism so two runs of the same
    season replay identically (required for C.8.2 reproducibility).

    Verified by C.4.1.
    """
    rng = random.Random(rng_seed)
    ids = list(gene_ids)
    rng.shuffle(ids)
    if len(ids) % 2 == 1:
        ids.pop()
    return [(ids[i], ids[i + 1]) for i in range(0, len(ids), 2)]


def update_scores(
    pair: tuple[str, str],
    *,
    winner_idx: int = 0,
    win_delta: float = DEFAULT_WIN_DELTA,
    loss_delta: float = DEFAULT_LOSS_DELTA,
) -> BattleResult:
    """Apply Arena score update.

    Defaults follow ADR-215 (`win +0.1`, `loss -0.05`).

    The `winner_idx` (0 or 1) lets callers inject Fitness-based winner
    selection; default 0 keeps the function pure / deterministic for
    the C.4.2 unit test. Stage 2 R4+ will route real `compute_fitness`
    output into this parameter via `run_arena`.

    Verified by C.4.2.
    """
    if winner_idx not in (0, 1):
        raise ValueError(f"winner_idx must be 0 or 1, got {winner_idx}")
    loser_idx = 1 - winner_idx
    return BattleResult(
        winner_id=pair[winner_idx],
        loser_id=pair[loser_idx],
        delta_score_winner=win_delta,
        delta_score_loser=loss_delta,
    )


def compute_fitness(
    c_util: float,
    r_rob: float,
    a_complete: float,
) -> float:
    """F(g) = C_util × R_rob × A_complete  (Spec §5.1 multiplicative model).

    **Strict-Test** per C.4.3 — multiplicative model is a hard Spec invariant:
    any single dimension collapsing to 0 collapses F(g) to 0 (no compensation
    by other dimensions). This is the protocol-level signal that all three
    quality axes must be non-trivially satisfied.
    """
    return c_util * r_rob * a_complete


def compute_diversity_factor(
    gene_shares: Iterable[float],
    *,
    alpha: float = 0.5,
) -> float:
    """`diversity_factor` mirroring Cloud SQL `get_display_fitness` (HHI-based).

    Formula:
        HHI = Σ share_i²                              # concentration index
        normalized_HHI = (HHI - 1/n) / (1 - 1/n)      # rescale to [0, 1]
        diversity = (1 - normalized_HHI) ** alpha     # alpha softens the curve
        return max(diversity, DIVERSITY_FLOOR)        # SQL floor 0.1

    Boundary cases:
        - n ≤ 1 → 1.0 (no diversity to measure)
        - uniform shares ([1/n]×n) → normalized_HHI = 0 → diversity = 1.0
        - fully concentrated ([1, 0×(n-1)]) → normalized_HHI = 1 → floor 0.1

    `alpha` ∈ [0, 1] controls how sharply diversity drops as concentration
    rises. alpha=1 is linear (1 - normalized_HHI); alpha<1 (default 0.5)
    keeps the curve flatter near the uniform end. Default matches the
    initial Cloud SQL configuration (config.diversity_factor_alpha).

    Verified by C.4.5 (cross-implementation consistency with SQL).
    """
    shares = list(gene_shares)
    n = len(shares)
    if n <= 1:
        return 1.0
    hhi = sum(s * s for s in shares)
    normalized_hhi = (hhi - 1 / n) / (1 - 1 / n)
    diversity = (1 - normalized_hhi) ** alpha
    return max(diversity, DIVERSITY_FLOOR)


def run_arena(gene_ids: Sequence[str], *, rng_seed: int) -> list[BattleResult]:
    """Run one Arena round over the given Gene set.

    Empty input → empty list (C.4.4 — no exception, total function).
    Single Gene → empty list (odd-count rest rule consumes the lone Gene).

    Default winner selection is pair[0] (deterministic) — stage 2 R4+ will
    inject `compute_fitness` comparison once the DeveloperAgent track ships.
    """
    if not gene_ids:
        return []
    pairs = pair_genes(gene_ids, rng_seed=rng_seed)
    return [update_scores(pair) for pair in pairs]

"""Season management — mirrors Cloud SQL `reset_season()` RPC.

Stage 2 R6: ``reset_season`` + ``run_many_seasons`` implemented.

Verified by tests/test_season.py (C.6.1–C.6.3). C.6.4 Python↔SQL parity
remains skip-on-no-psycopg / xfail until the Cloud SQL fixture lands.

**Cross-implementation invariant** (Strict-Test C.6.4, deferred):
    Same input → same output as SQL `reset_season()` RPC.

Design notes:
    - ``archive[i].final_score`` stores the **raw** end-of-season score
      (no half-life applied). C.6.1 explicitly asserts this — archive is
      the immutable historical record (used for leaderboard / replay).
    - ``archive[i].final_fitness`` stores the **decayed** value
      (``score × fitness_retention_rate``); this is the per-Gene starting
      adaptation for the next season's Arena, mirroring the dual-track
      semantics in Cloud SQL (``season_archives.final_score`` vs
      ``genes.next_season_starting_fitness``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

DEFAULT_FITNESS_RETENTION_RATE = 0.5
DEFAULT_DURATION_DAYS = 90


@dataclass
class SeasonState:
    season_number: int
    started_step: int
    config: dict = field(default_factory=dict)
    status: str = "active"
    ended_step: Optional[int] = None


@dataclass
class SeasonArchiveEntry:
    season_id: int
    gene_id: str
    final_rank: int
    final_score: float
    final_fitness: float


def reset_season(
    current: SeasonState,
    *,
    gene_scores: dict[str, float],
    new_season_started_step: int,
    fitness_retention_rate: float = DEFAULT_FITNESS_RETENTION_RATE,
) -> tuple[SeasonState, list[SeasonArchiveEntry]]:
    """End the current season → archive → start a new one.

    Pure-functional: ``current`` is *not* mutated. Caller wishing to mark
    the old season's ``status`` / ``ended_step`` should do so explicitly
    after consuming the archive (e.g. for SQL UPDATE batching).

    Archive ranking is by ``final_score`` descending, 1-based — ties
    broken by ``gene_id`` lexicographic ordering for deterministic
    replay (C.6.4 parity dependency).

    Verified by C.6.1 / C.6.2; C.6.4 SQL parity deferred.
    """
    sorted_genes = sorted(
        gene_scores.items(),
        key=lambda kv: (-kv[1], kv[0]),
    )
    archive = [
        SeasonArchiveEntry(
            season_id=current.season_number,
            gene_id=gene_id,
            final_rank=rank,
            final_score=score,
            final_fitness=score * fitness_retention_rate,
        )
        for rank, (gene_id, score) in enumerate(sorted_genes, start=1)
    ]

    new_state = SeasonState(
        season_number=current.season_number + 1,
        started_step=new_season_started_step,
        config=dict(current.config),
        status="active",
        ended_step=None,
    )
    return new_state, archive


def run_many_seasons(initial: SeasonState, *, n: int) -> SeasonState:
    """Sequentially run ``n`` season resets — used by C.6.3 stability test.

    Empty ``gene_scores`` per iteration: this driver only exercises the
    monotonic season-number increment + state-rollover path, not score
    decay (which is unit-tested in C.6.1). Each season advances
    ``started_step`` by the current state's ``config["duration_steps"]``
    (default 90) so the timeline is well-formed for any downstream
    Arena schedule.

    Raises ``ValueError`` for negative ``n`` (defensive — total function
    convention shared with reputation.apply_decay).
    """
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n}")
    state = initial
    for _ in range(n):
        duration = state.config.get("duration_steps", DEFAULT_DURATION_DAYS)
        state, _ = reset_season(
            current=state,
            gene_scores={},
            new_season_started_step=state.started_step + duration,
        )
    return state

"""Ecosystem metrics — HHI, Gini, newcomer entry rate.

Stage 2 R4: pure-stat impls for HHI / Gini / top-N newcomer rate /
Shannon diversity. Verified by tests/test_metrics.py (C.7.1–C.7.4).
"""

from __future__ import annotations

import math
from typing import Iterable, Mapping

HHI_SCALE = 10000.0


def hhi(shares: Iterable[float]) -> float:
    """Herfindahl–Hirschman Index, scaled to [0, 10000].

    Formula: HHI = (Σ share_i²) × 10000.

    Boundaries:
        - Fully concentrated (one share = 1.0)  → 10000
        - Fully uniform ([1/n]×n)              → 10000 / n
        - Empty input                          → 0 (C.7.4 graceful)

    The 10000 scale follows the antitrust convention (DOJ/EC). For
    diversity calculations elsewhere we use the unscaled HHI (Σ s²),
    e.g. `arena.compute_diversity_factor`.
    """
    values = list(shares)
    if not values:
        return 0.0
    return sum(s * s for s in values) * HHI_SCALE


def gini(values: Iterable[float]) -> float:
    """Gini coefficient ∈ [0, 1].

    Formula (Lorenz-curve form, sorted):
        G = Σ_i (2·i − n + 1) · x_i  /  (n · Σ x)

    Boundaries:
        - Fully equal      → 0   (verified C.7.2)
        - One non-zero/n=N → (n-1)/n   (approaches 1 for large n, verified
                                        C.7.2 with abs tolerance 0.02 at n=100)
        - Empty / all-zero → 0 (avoids divide-by-zero, C.7.4 graceful)
    """
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        return 0.0
    total = sum(vals)
    if total == 0:
        return 0.0
    cum = sum((2 * i - n + 1) * x for i, x in enumerate(vals))
    return cum / (n * total)


def top_n_newcomer_rate(
    top_n_author_ages_days: Mapping[str, int],
    *,
    newcomer_window_days: int = 30,
) -> float:
    """Share of authors among Top-N whose first publish ≤ window_days ago.

    Input is a mapping author_id → days_since_first_publish for the Top-N
    authors (caller pre-filters Top-N upstream). Empty mapping → 0.0.

    Verified by C.7.3 — Q3 acceptance criterion ("Top-10 newcomer rate
    ≥ 30% at season N for a healthy newcomer pipeline").
    """
    if not top_n_author_ages_days:
        return 0.0
    newcomers = sum(
        1 for days in top_n_author_ages_days.values()
        if days <= newcomer_window_days
    )
    return newcomers / len(top_n_author_ages_days)


def shannon_diversity(shares: Iterable[float]) -> float:
    """Shannon diversity index — complementary signal to HHI.

    Formula: H = -Σ p_i · ln(p_i)  (natural log; zero shares skipped to
    avoid log(0) singularity).

    H = 0 when fully concentrated; H = ln(n) when fully uniform over n.
    Not directly tested by C.7 but used by C.6 long-run stability checks.
    """
    values = [s for s in shares if s > 0]
    if not values:
        return 0.0
    return -sum(p * math.log(p) for p in values)

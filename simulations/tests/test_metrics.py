"""C.7 — Ecosystem metrics tests.

TDD red phase.
"""

from __future__ import annotations

import math

import pytest


# ---------------------------------------------------------------------------
# C.7.1 — HHI: concentrated vs uniform
# ---------------------------------------------------------------------------
def test_C_7_1_hhi_fully_concentrated() -> None:
    """C.7.1 — single 1.0 share ⇒ HHI = 10000."""
    from src.metrics import hhi

    assert hhi([1.0]) == pytest.approx(10000.0)
    assert hhi([1.0, 0.0, 0.0, 0.0]) == pytest.approx(10000.0)


def test_C_7_1_hhi_fully_uniform() -> None:
    """C.7.1 — uniform shares ⇒ HHI = 10000 / n."""
    from src.metrics import hhi

    n = 10
    shares = [1 / n] * n
    assert hhi(shares) == pytest.approx(10000.0 / n)


# ---------------------------------------------------------------------------
# C.7.2 — Gini extremes
# ---------------------------------------------------------------------------
def test_C_7_2_gini_fully_equal() -> None:
    """C.7.2 — fully equal distribution ⇒ Gini = 0."""
    from src.metrics import gini

    assert gini([1.0] * 100) == pytest.approx(0.0, abs=1e-6)


def test_C_7_2_gini_fully_concentrated() -> None:
    """C.7.2 — single non-zero value ⇒ Gini → 1 (n large)."""
    from src.metrics import gini

    values = [0.0] * 99 + [1.0]
    assert gini(values) == pytest.approx(1.0, abs=0.02)


# ---------------------------------------------------------------------------
# C.7.3 — Top-10 newcomer rate
# ---------------------------------------------------------------------------
def test_C_7_3_top10_newcomer_rate() -> None:
    """C.7.3 — Top-10 with 3 authors ≤30 days ⇒ rate = 0.3."""
    from src.metrics import top_n_newcomer_rate

    ages = {f"dev-{i}": (5 if i < 3 else 90) for i in range(10)}
    rate = top_n_newcomer_rate(ages, newcomer_window_days=30)
    assert rate == pytest.approx(0.3)


# ---------------------------------------------------------------------------
# C.7.4 — graceful on empty input
# ---------------------------------------------------------------------------
def test_C_7_4_metrics_empty_input() -> None:
    """C.7.4 — HHI/Gini/newcomer-rate return 0 or NaN, never crash."""
    from src.metrics import gini, hhi, top_n_newcomer_rate

    for fn_call in (lambda: hhi([]), lambda: gini([]), lambda: top_n_newcomer_rate({})):
        result = fn_call()
        assert (
            result == 0
            or result == 0.0
            or (isinstance(result, float) and math.isnan(result))
        ), f"empty input must return 0 / NaN, got {result!r}"

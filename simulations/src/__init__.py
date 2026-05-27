"""Rotifer Protocol ABM Simulations — v0.9 stage 1 (TDD scaffold).

This package mirrors the protocol's economic logic in Python so that
agent-based simulations can calibrate parameters before they are pinned
into Cloud SQL / Spec.

All public surface is intentionally unimplemented (`raise NotImplementedError`)
so the corresponding pytest suite stays red until stage 2 implementation
turns each function green one by one.
"""

__version__ = "0.9.0-dev"
__all__ = [
    "model",
    "arena",
    "reputation",
    "season",
    "metrics",
    "agents",
]

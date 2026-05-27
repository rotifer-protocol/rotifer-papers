"""ABM main model — orchestrates Gene / Developer agents through Arena + Season.

Stage 2 R7: end-to-end ``RotiferModel.step`` / ``run`` + YAML ``load_config``
+ ``DeveloperAgent.step`` probabilistic publication trigger implemented.

Verified by tests/test_model.py (C.8.1–C.8.3 turn green; C.8.4 hits the
existing in-test ``pytest.skip``; C.8.5 remains skip-on-no-memory_profiler).

Design notes (per S2-L4):
    - ``schedule`` is a ``SimpleNamespace(steps=0)`` we advance manually each
      step; we do **not** use ``mesa.time.RandomActivation`` because Gene
      step is order-sensitive (Arena must write ``usage_this_step`` before
      ``GeneAgent.step`` reads/pops it).
    - Determinism: every random draw flows through ``self.random`` (model)
      or ``self.model.random`` (agents); ``mesa.Model(seed=...)`` seeds
      both. List/dict iteration follows insertion order. Pair-RNG seeds
      are derived deterministically from ``self.random.randint`` per step.
    - ``DeveloperAgent.step`` returns the freshly-published Gene (or None);
      ``RotiferModel.step`` collects it into ``self.genes`` so the next
      Arena round sees the new Gene.
"""

from __future__ import annotations

import argparse
import random as _random
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import mesa
import yaml

from .agents import DeveloperAgent, GeneAgent, Strategy
from .arena import (
    BattleResult,
    compute_diversity_factor,
    compute_fitness,
    pair_genes,
    update_scores,
)
from .metrics import gini, hhi, shannon_diversity, top_n_newcomer_rate
from .season import SeasonState, reset_season

DEV_PUBLISH_PROBABILITY = 1.0 / 30.0  # ~1 publish per developer per 30 steps.
ARENA_QUALITY_CONSTANT = 0.9  # c_util & a_complete proxies; r_rob = gene.fitness.
TOP_N_NEWCOMERS = 10

DAYS_PER_STEP = 3  # 90-day season ÷ 30-step season = 3 days/step (per baseline.yaml).

INSTALL_DEV_UID_BASE = 10_000
CARR_DEV_UID_BASE = 20_000


@dataclass
class ModelConfig:
    """Validated config object — built from YAML.

    Time semantics: ``n_steps_per_season`` is the simulation-clock counter
    (used internally by ``RotiferModel.step``); ``season_length_days`` is
    the human-friendly knob that the Q3 sweep targets. The two are linked
    by ``DAYS_PER_STEP`` (3 days per step, per baseline.yaml notes). The
    sweep runner's ``override_config`` keeps them in sync when you target
    ``season_length_days`` — see ``src/sweep_runner.py``.
    """

    n_genes: int
    n_developers: int
    n_seasons: int
    n_steps_per_season: int
    seed: int

    alpha: float = 0.5
    decay_per_month: float = 0.05
    decay_floor: float = 0.01

    fitness_retention_rate: float = 0.5
    newcomer_protection_days: int = 30
    newcomer_bonus_multiplier: float = 1.5
    season_length_days: int = 90

    developer_strategy_mix: dict[Strategy, float] = field(
        default_factory=lambda: {Strategy.INSTALL: 1.0}
    )

    raw: dict[str, Any] = field(default_factory=dict)


def _merge_yaml_with_extends(path: Path) -> dict[str, Any]:
    """Load YAML and recursively merge any ``extends:`` parent.

    Child keys override parent keys (shallow merge — sufficient for v0.9
    sweep configs which only override scalars / top-level lists).
    """
    path = Path(path).resolve()
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    parent_ref = data.pop("extends", None)
    if parent_ref is None:
        return data

    parent_path = (path.parent / parent_ref).resolve()
    parent = _merge_yaml_with_extends(parent_path)
    parent.update(data)
    return parent


def load_config(path: str | Path) -> ModelConfig:
    """Parse a YAML config into ``ModelConfig`` (with ``extends:`` support).

    Verified by C.8.3 (sweep_q2.yaml inherits from baseline.yaml + adds
    a ``sweep`` block; ``raw`` retains the merged dict so caller can
    drive parameter sweeps).
    """
    raw = _merge_yaml_with_extends(Path(path))

    strategy_mix_raw = raw.get("developer_strategy_mix", {"install": 1.0})
    strategy_mix: dict[Strategy, float] = {}
    for key, value in strategy_mix_raw.items():
        try:
            strategy_mix[Strategy(key)] = float(value)
        except ValueError as exc:
            raise ValueError(f"Unknown developer strategy: {key!r}") from exc

    n_steps_per_season = int(raw["n_steps_per_season"])
    season_length_days = int(raw.get("season_length_days", n_steps_per_season * DAYS_PER_STEP))

    return ModelConfig(
        n_genes=int(raw["n_genes"]),
        n_developers=int(raw["n_developers"]),
        n_seasons=int(raw["n_seasons"]),
        n_steps_per_season=n_steps_per_season,
        seed=int(raw.get("seed", 42)),
        alpha=float(raw.get("alpha", 0.5)),
        decay_per_month=float(raw.get("decay_per_month", 0.05)),
        decay_floor=float(raw.get("decay_floor", 0.01)),
        fitness_retention_rate=float(raw.get("fitness_retention_rate", 0.5)),
        newcomer_protection_days=int(raw.get("newcomer_protection_days", 30)),
        newcomer_bonus_multiplier=float(raw.get("newcomer_bonus_multiplier", 1.5)),
        season_length_days=season_length_days,
        developer_strategy_mix=strategy_mix,
        raw=raw,
    )


class RotiferModel(mesa.Model):
    """ABM main model — orchestrates the full economic loop.

    Lifecycle per ``step()``:
        1. Arena round (pair genes, decide winner by ``compute_fitness``).
        2. Apply battle deltas to ``self.gene_scores``; tag winner Genes
           with ``usage_this_step = 1`` for the post-Arena ``gene.step()``.
        3. ``gene.step()`` for every Gene — usage growth or idle decay.
        4. ``dev.step()`` for every Developer — probabilistic publish;
           returned Gene (if any) appended to ``self.genes``.
        5. Increment ``self.schedule.steps``.
        6. If ``steps_into_season >= n_steps_per_season`` → ``reset_season``
           (archive the season + decay carryover scores by retention_rate).
    """

    def __init__(self, config: ModelConfig) -> None:
        super().__init__(seed=config.seed)
        # mesa.Model.__new__ pulls seed from instantiation **kwargs, not from
        # super().__init__(seed=...). Since the test calls RotiferModel(config)
        # without forwarding seed= to the instantiation, mesa otherwise falls
        # back to a global random.random() draw (process-state pollution → C.8.2
        # non-determinism). Override self.random explicitly to honour cfg.seed.
        self.random = _random.Random(config.seed)
        self.config = config
        self.schedule = types.SimpleNamespace(steps=0)
        self.genes: list[GeneAgent] = []
        self.developers: list[DeveloperAgent] = []
        self.battle_history: list[BattleResult] = []
        self.season_archive_history: list[Any] = []

        self.current_season: SeasonState = SeasonState(
            season_number=1,
            started_step=0,
            config={
                "fitness_retention_rate": config.fitness_retention_rate,
                "duration_steps": config.n_steps_per_season,
            },
        )
        self.gene_scores: dict[str, float] = {}
        self.gene_first_publish_step: dict[str, int] = {}
        self.gene_author: dict[str, str] = {}

        self._init_developers()
        self._init_genes()

    # -- initialisation --------------------------------------------------

    def _init_developers(self) -> None:
        mix = self.config.developer_strategy_mix
        n_install = int(round(self.config.n_developers * mix.get(Strategy.INSTALL, 0.0)))
        n_carr = self.config.n_developers - n_install

        for i in range(n_install):
            dev = DeveloperAgent(
                unique_id=INSTALL_DEV_UID_BASE + i,
                model=self,
                developer_id=f"dev-install-{i:04d}",
                strategy=Strategy.INSTALL,
            )
            self.developers.append(dev)
        for i in range(n_carr):
            dev = DeveloperAgent(
                unique_id=CARR_DEV_UID_BASE + i,
                model=self,
                developer_id=f"dev-carr-{i:04d}",
                strategy=Strategy.CARR,
            )
            self.developers.append(dev)

    def _init_genes(self) -> None:
        if not self.developers:
            return
        for i in range(self.config.n_genes):
            dev = self.developers[i % len(self.developers)]
            base_fitness = self.random.uniform(0.3, 0.7)
            domain = f"d-{i % 5}"
            gene = dev.publish_gene(domain=domain, base_fitness=base_fitness)
            self._register_gene(gene)

    def _register_gene(self, gene: GeneAgent) -> None:
        self.genes.append(gene)
        self.gene_scores[gene.gene_id] = 0.0
        self.gene_first_publish_step[gene.gene_id] = gene.created_step
        self.gene_author[gene.gene_id] = gene.author_id

    # -- main loop -------------------------------------------------------

    def step(self) -> None:
        round_results = self._run_arena_round()
        winner_ids: set[str] = set()
        for result in round_results:
            self.battle_history.append(result)
            self.gene_scores[result.winner_id] += result.delta_score_winner
            self.gene_scores[result.loser_id] += result.delta_score_loser
            winner_ids.add(result.winner_id)

        for gene in self.genes:
            if gene.gene_id in winner_ids:
                gene.state.metadata["usage_this_step"] = 1
            gene.step()

        for dev in self.developers:
            new_gene = dev.step()
            if new_gene is not None:
                self._register_gene(new_gene)

        self.schedule.steps += 1

        steps_into_season = self.schedule.steps - self.current_season.started_step
        if steps_into_season >= self.config.n_steps_per_season:
            self._end_season()

    def _run_arena_round(self) -> list[BattleResult]:
        if len(self.genes) < 2:
            return []
        gene_ids = [g.gene_id for g in self.genes]
        fitness_map = {g.gene_id: g.fitness for g in self.genes}
        pair_seed = self.random.randint(0, 2**31 - 1)
        pairs = pair_genes(gene_ids, rng_seed=pair_seed)

        results: list[BattleResult] = []
        for pair in pairs:
            id_a, id_b = pair
            f_a = compute_fitness(
                c_util=ARENA_QUALITY_CONSTANT,
                r_rob=fitness_map[id_a],
                a_complete=ARENA_QUALITY_CONSTANT,
            )
            f_b = compute_fitness(
                c_util=ARENA_QUALITY_CONSTANT,
                r_rob=fitness_map[id_b],
                a_complete=ARENA_QUALITY_CONSTANT,
            )
            winner_idx = 0 if f_a >= f_b else 1
            results.append(update_scores(pair, winner_idx=winner_idx))
        return results

    def _end_season(self) -> None:
        new_state, archive = reset_season(
            current=self.current_season,
            gene_scores=dict(self.gene_scores),
            new_season_started_step=self.schedule.steps,
            fitness_retention_rate=self.config.fitness_retention_rate,
        )
        self.season_archive_history.append(archive)
        self.current_season = new_state
        retention = self.config.fitness_retention_rate
        for gid in list(self.gene_scores.keys()):
            self.gene_scores[gid] *= retention

    # -- run + final metrics --------------------------------------------

    def run(self) -> dict[str, Any]:
        """Run for ``config.n_seasons * config.n_steps_per_season`` steps.

        Returns aggregated metrics — verified deterministic in C.8.2 by
        running twice from a fresh ``RotiferModel(config)`` and asserting
        sha256 equality of the JSON-serialised result.
        """
        total_steps = self.config.n_seasons * self.config.n_steps_per_season
        for _ in range(total_steps):
            self.step()
        return self._compute_final_metrics()

    def _compute_final_metrics(self) -> dict[str, Any]:
        if not self.genes:
            return {
                "HHI": 0.0,
                "gini": 0.0,
                "top10_newcomer_rate": 0.0,
                "diversity_factor": 1.0,
                "shannon_diversity": 0.0,
                "top10_share": 0.0,
                "average_first_publish_to_top10_days": 0.0,
                "n_genes_final": 0,
                "n_seasons_completed": max(0, self.current_season.season_number - 1),
                "total_battles": len(self.battle_history),
            }

        fitnesses = [g.fitness for g in self.genes]
        total = sum(fitnesses) or 1.0
        shares = [f / total for f in fitnesses]

        top_n = sorted(
            self.genes,
            key=lambda g: g.fitness,
            reverse=True,
        )[:TOP_N_NEWCOMERS]
        protection_days = self.config.newcomer_protection_days
        # Bug fix (Stage-3 R9): metrics.top_n_newcomer_rate expects days
        # (parameter name top_n_author_ages_days). Earlier R7 implementation
        # passed raw steps, which made the rate a constant 0 across all
        # season lengths once the simulation horizon exceeded a few seasons
        # (≪ 30-day newcomer window after × DAYS_PER_STEP). Convert here so
        # the rate metric carries the unit metrics.py declares.
        top_n_ages = {
            self.gene_author[g.gene_id]: max(
                0,
                (self.schedule.steps - self.gene_first_publish_step[g.gene_id])
                * DAYS_PER_STEP,
            )
            for g in top_n
        }
        top_n_share = sum(g.fitness for g in top_n) / total

        top_n_age_steps = [
            max(0, self.schedule.steps - self.gene_first_publish_step[g.gene_id])
            for g in top_n
        ]
        if top_n_age_steps:
            avg_age_steps = sum(top_n_age_steps) / len(top_n_age_steps)
            avg_first_publish_to_top10_days = avg_age_steps * DAYS_PER_STEP
        else:
            avg_first_publish_to_top10_days = 0.0

        return {
            "HHI": hhi(shares),
            "gini": gini(shares),
            "top10_newcomer_rate": top_n_newcomer_rate(
                top_n_ages,
                newcomer_window_days=protection_days,
            ),
            "diversity_factor": compute_diversity_factor(
                shares,
                alpha=self.config.alpha,
            ),
            "shannon_diversity": shannon_diversity(shares),
            "top10_share": top_n_share,
            "average_first_publish_to_top10_days": avg_first_publish_to_top10_days,
            "n_genes_final": len(self.genes),
            "n_seasons_completed": max(0, self.current_season.season_number - 1),
            "total_battles": len(self.battle_history),
        }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Rotifer ABM simulations")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--output", default="reports/", help="Output directory")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    model = RotiferModel(config)
    model.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

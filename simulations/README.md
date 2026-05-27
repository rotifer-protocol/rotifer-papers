# Rotifer Protocol — ABM Simulations

Agent-Based Model (ABM) simulations for **Rotifer Protocol** economic parameter calibration.

This directory satisfies **plan v0.9 §3.4 (ABM 仿真验证)** — Apache 2.0, fully reproducible.

> **Status (2026-05-27)**: v0.9 阶段 3 完成 — framework + tests + Q1–Q4 sweeps (1250 total ABM runs) all done.

## 1. Project layout

```
simulations/
├── README.md                ← This file
├── LICENSE                  ← Apache 2.0
├── requirements.txt         ← Python dependencies
├── pyproject.toml           ← Project metadata + pytest config
├── src/
│   ├── model.py             ← ABM main model (orchestrator)
│   ├── arena.py             ← Arena battle engine
│   ├── reputation.py        ← Reputation computation (mirrors Cloud SQL)
│   ├── season.py            ← Season management (reset + half-life)
│   ├── metrics.py           ← HHI / Gini / newcomer entry rate
│   └── agents/
│       ├── gene_agent.py    ← Gene Agent (publish / decay / battle)
│       └── developer_agent.py ← Developer Agent (install vs carr strategy)
├── configs/
│   ├── baseline.yaml        ← Baseline parameters
│   ├── sweep_q1.yaml        ← Q1 (Nash equilibrium for α) parameter sweep
│   ├── sweep_q2.yaml        ← Q2 (diversity_factor) parameter sweep
│   ├── sweep_q3.yaml        ← Q3 (season length) parameter sweep
│   └── sweep_q4.yaml        ← Q4 (decay stability) parameter sweep
├── notebooks/               ← Jupyter notebooks for each Q
├── reports/                 ← Final reports + figures + data
└── tests/                   ← pytest suite (~45 tests, see v0.9-stage-1-tdd-test-cases.md)
```

## 2. Setup

```bash
cd simulations/
python3.11 -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## 3. Run

### 3.1 Baseline simulation

```bash
python -m src.model --config configs/baseline.yaml
```

### 3.2 Parameter sweep

```bash
python -m src.model --config configs/sweep_q2.yaml --output reports/q2_results/
```

### 3.3 Tests

```bash
# All tests
pytest

# Only unit (skip integration / slow)
pytest -m "not integration and not slow"

# Only Strict-Test cases (per ADR-264 §5)
pytest -m strict_test

# Property-based tests with verbose hypothesis output
pytest -m property --hypothesis-show-statistics

# With coverage
pytest --cov=src --cov-report=html
```

## 4. Simulation problems (Q1–Q4)

| Q | Question | Tier | Stage |
|---|---|---|---|
| Q1 | Arena Nash equilibrium — best `α` for `diversity_factor`? | Tier 2 (500 Gene × 100 runs) | stage 2 |
| Q2 | `diversity_factor` — does usage_diversity × path_diversity prevent winner-take-all? | Tier 1 (200 Gene × 50 runs) | stage 2 |
| Q3 | Season length (30/60/90/120/180 days) — newcomer entry rate? | Tier 1 (200 Gene × 50 runs) | stage 2 |
| Q4 | Reputation decay floor (0.01 vs 0.20) — long-run stability? | Tier 2 (500 Gene × 100 runs) | stage 3 |
| Q2.5 | Carr vs install strategies (ADR-260 C3) — adaptive value? | Tier 1 | stage 3 |

> **Tier 3 (academic-grade, 2000 Gene × 1000 runs)** is deferred to v1.0+ paper publication.

## 5. Reproducibility

- All simulation runs **must** specify `seed` in config — same seed → same metrics.
- Strict-Test case `C.8.2` enforces sha256 frozen-parity on metrics output.
- Final reports include the sha256 of `metrics.json` so independent reviewers can verify.

## 6. Cross-implementation consistency

Some components mirror Cloud SQL (Supabase) logic and **must** stay byte-equivalent:

| Python | SQL counterpart | Strict-Test ID |
|---|---|---|
| `reputation.py::compute()` | `compute_all_reputations()` RPC | C.5.5 |
| `season.py::reset_season()` | `reset_season()` RPC | C.6.4 |
| `arena.py::compute_fitness()` | `get_display_fitness()` function | C.4.5 |

Cross-implementation parity is **deferred to stage 2** — stage 1 only marks the test scaffold (`@pytest.mark.skip(reason="awaiting Cloud impl")`).

## 7. Sweep engineering practice (per ADR-281 D3 + D6)

Established 2026-05-19 after the v0.9 §3.4 Stage-3 sweeps (C-R10 / R11 / R12, 1250 ABM runs total) revealed two failure modes that future sweeps **must** prevent up front. See ADR-281 (vestigial parameters & model-realization gap) for the full meta-finding.

### 7.1 Mechanism-engagement check (D3) — pre-sweep gate

Before launching any parameter sweep, **verify that the swept mechanism has a non-trivial engagement condition under the current ABM state**. A sweep on a mechanism that never fires wastes compute and produces "vestigial parameter" results that look statistically clean but carry zero signal.

Required check, per parameter family:

| Parameter | Engagement condition (must hold during the sweep) | How to verify |
|---|---|---|
| `alpha` (`diversity_factor` exponent) | `(1 - normalized_HHI) < 1.0` on a non-trivial fraction of Arena steps (i.e. some market concentration exists) | Run a baseline (1 run, ~30 seasons) and grep `diversity_factor` log column — confirm values < 1.0 occur |
| `decay_floor` (reputation lower bound) | Some Gene reputations decay near the sweep range upper bound (e.g. for `decay_floor ∈ [0.01, 0.20]`, some reputations should reach < 0.20) | Run a baseline + dump reputation distribution at season-end — confirm tail extends below sweep `max(decay_floor)` |
| `tau` / `V_min` (publishing thresholds) | Some Genes have `F(g)` or `V(g)` in the sweep range (i.e. the threshold actually rejects some Genes) | Run baseline publishing flow, log distribution of `F(g)` / `V(g)`, confirm overlap with sweep range |

The check is cheap (1 baseline run, ~30 seconds at Tier-0 / ~5 minutes at Tier-1) compared to a full Tier-2 sweep (~1.5-3 hours). The sweep YAML's header comment **should** declare which engagement evidence has been verified.

If the check fails (mechanism does not engage), **do not run the sweep**. Either (a) fix the underlying ABM state first (e.g. wait for E1 newcomer_bonus routing per v0.9 D-04 / v1.0 §4.5.X), or (b) explicitly redesign the sweep to test the engagement condition itself rather than the parameter scan.

### 7.2 Sweep YAML hygiene (D6) — pre-commit smoke test

`metrics_of_interest` field names in sweep YAMLs **must** match the actual ABM output column names produced by `sweep_runner.py`. A mismatch silently leaves `summary.json::per_value` empty (data is still recoverable from `results.csv`, but is a hygiene failure that hides per-value statistics from quick review).

Standard practice for any new or modified sweep YAML:

```bash
# 1. Smoke test (1 run, ~30 seconds)
python -m src.sweep_runner --config configs/sweep_qX.yaml --limit-runs 1

# 2. Verify summary.json per_value is populated
jq '.per_value | to_entries | map(.value | length)' reports/qX_*/summary.json
# Each entry should be > 0 (count of metrics actually summarized)

# 3. Only then commit the YAML
git add configs/sweep_qX.yaml
```

A real-world example of this hygiene failure is the C-R12 Q4 sweep (`configs/sweep_q4.yaml`, fixed 2026-05-19) — `metrics_of_interest` declared three fictional column names (`reputation_variance_long_run` / `reputation_floor_violations` / `active_gene_count_long_run`) that did not exist in the model output. Per ADR-281 D6 the file now uses `gini` / `HHI` / `shannon_diversity` (real keys).

### 7.3 Audit trail

Each sweep report (`reports/qX_*/report.md`) **should** explicitly state:

1. Which engagement check (§7.1) was performed and the outcome
2. Whether the smoke test (§7.2) was run before commit
3. Whether the swept parameter is judged **non-vestigial** (sweep produces statistically detectable behavioral change) or **vestigial** (no detectable change, mechanism never engaged)

Reports for vestigial parameters are still valuable — they are diagnostic signals about the ABM's realization vs the protocol's design intent. They should not be discarded or re-run with bigger sample sizes; that only adds spurious precision.

## 8. References

- **Plan**: Rotifer Protocol v0.9 Plan §3.4
- **Vision Roadmap**: §5.6 (economic system)
- **ADR-035**: ABM simulation strategy
- **ADR-260 C3 / C6**: Carr training × adaptive exploration
- **ADR-281**: Vestigial parameters & model-realization gap

## 9. License

Apache License 2.0 — see [`LICENSE`](./LICENSE).

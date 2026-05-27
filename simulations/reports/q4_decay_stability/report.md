# Q4 Reputation Decay Long-Run Stability — C-R12 ABM Sweep Report

**Simulation run**: 2026-05-19 12:12 → 2026-05-19 15:57 (UTC+8)  
**Duration**: 3h 46min | **Total runs**: 500 (5 decay_floor × 100 runs)  
**Scale**: Tier 2 — n_genes=500, n_developers=100, n_seasons=100  
**Config**: `configs/sweep_q4.yaml`

---

## 1. Verification Criterion

> **Q4**: 声誉衰减函数的长期稳定性  
> **Acceptance**: 100 赛季后声誉基尼系数 < 0.6  
> **Sweep parameter**: `decay_floor` ∈ {0.01, 0.05, 0.10, 0.15, 0.20}

---

## 2. Results

### 2.1 Core Metrics

| decay_floor | gini mean ± std    | CI95     | HHI mean | n_genes_final | Shannon |
|-------------|--------------------|----------|----------|---------------|---------|
| 0.01        | 0.1353 ± 0.0008    | ±0.00015 | 1.0603   | 10499         | 9.1689  |
| 0.05        | 0.1353 ± 0.0007    | ±0.00014 | 1.0597   | 10505         | 9.1694  |
| 0.10        | 0.1353 ± 0.0008    | ±0.00015 | 1.0595   | 10508         | 9.1697  |
| 0.15        | 0.1352 ± 0.0007    | ±0.00013 | 1.0601   | 10501         | 9.1690  |
| 0.20        | 0.1355 ± 0.0007    | ±0.00014 | 1.0589   | 10514         | 9.1702  |

All 500 runs completed full 100 seasons.

### 2.2 Acceptance Check

| decay_floor | runs satisfying gini < 0.6 | gini mean | gini max | gini min |
|-------------|----------------------------|-----------|----------|----------|
| 0.01        | **100 / 100 ✅**           | 0.1353    | 0.1368   | 0.1334   |
| 0.05        | **100 / 100 ✅**           | 0.1353    | 0.1373   | 0.1338   |
| 0.10        | **100 / 100 ✅**           | 0.1353    | 0.1371   | 0.1334   |
| 0.15        | **100 / 100 ✅**           | 0.1352    | 0.1369   | 0.1331   |
| 0.20        | **100 / 100 ✅**           | 0.1355    | 0.1374   | 0.1337   |

> **Q4 acceptance: ✅ PASSED** — 500/500 runs (100%) satisfy gini < 0.6 after 100 seasons. Observed gini ≈ 0.135 sits at **22.5%** of the acceptance threshold; the system is far from the failure boundary.

### 2.3 Cross-decay_floor Pairwise Significance (vs 0.01 baseline)

| Comparison | Δ gini   | Pooled CI95 | Significant? |
|------------|----------|-------------|--------------|
| 0.01 vs 0.05 | -0.00003 | ±0.00021 | ❌ NOT significant |
| 0.01 vs 0.10 | +0.00005 | ±0.00021 | ❌ NOT significant |
| 0.01 vs 0.15 | -0.00010 | ±0.00020 | ❌ NOT significant |
| 0.01 vs 0.20 | +0.00017 | ±0.00020 | ❌ NOT significant |

**Cross-decay_floor variation (0.00026) ≈ max within-cell CI95 (0.00015)** — pairwise differences are all inside or at the noise floor.

---

## 3. Findings

### F1 — Verification Standard ✅ Met with Massive Headroom

The acceptance threshold (gini < 0.6) is over-satisfied by a factor of ~4.4. There is no risk of long-run reputation collapse into a few Genes — the population stays diverse across all 5 decay_floor settings.

### F2 — `decay_floor` is a Vestigial Parameter at Tier-2 Scale

Across 500 runs spanning the full 0.01-0.20 range (a 20× span), the gini variation is 0.00026 — essentially indistinguishable from sampling noise. Whether decay_floor is at the original v0.9 default (0.01) or at the spec-recommended (0.20), the long-run reputation distribution looks identical.

### F3 — Pattern Is Continuous With Q1 + Q2 Findings

This is the **third "vestigial parameter" finding** in C-track stage-3 sweeps:

| Sweep | Parameter | Runs | Outcome |
|-------|-----------|------|---------|
| C-R10 Q1 | alpha (Tier-2) | 500 | No effect within [0.1, 0.9] |
| C-R11 Q2 | alpha (boundary, incl. 0) | 250 | No effect even at α=0 |
| **C-R12 Q4** | **decay_floor** | **500** | **No effect within [0.01, 0.20]** |

Combined: **1250 runs across alpha + decay_floor — both tuning surfaces have no measurable behavioral expression.**

### F4 — Common Root Cause: ABM Market Pathologically Dispersed

All three findings converge on the same structural condition:

- top10_share ≈ 0.22% (Q2)
- diversity_factor ≡ 1 (Q2: dampening never engages)
- gini ≈ 0.135 (Q4: reputation already near-uniform; decay_floor has nothing to "floor")

When the population is already uniformly distributed, parameters designed to *limit concentration* (alpha) or *prevent collapse* (decay_floor) have no work to do. The current ABM cannot generate the conditions under which these mechanisms operate.

### F5 — E1 Remains the Cross-Cutting Unblocking Path

Just as for Q2 alpha re-test, Q4 decay_floor would only show differential behavior if the reputation distribution were genuinely concentrated to begin with. E1 (newcomer_bonus → Arena selection, deferred to v1.0 §4.5.X per D-04) is the same prerequisite. Once Top-10 holds non-trivial market share *and* genes circulate through it, both alpha and decay_floor will have meaningful expression.

---

## 4. Cross-Reference: Joint v0.9 §3.4 Stage-3 Picture

This sweep effectively closes v0.9 §3.4 Q4. Combined headline across §3.4 stage-3:

| Q | Original target | Acceptance | Vestigial finding |
|---|-----------------|-----------|-------------------|
| Q1 | F(g) Nash equilibrium | ✅ Stable equilibrium exists, insensitive to seeds | alpha vestigial in [0.1, 0.9] |
| Q2 | diversity_factor effectiveness | ❌ Falsified at boundary (alpha=0 indistinguishable from >0) | alpha vestigial including 0 |
| Q3 | Season length newcomer rate | ⚠️ Tier-1 unreachable; deferred Tier-2 to post-E1 | (R9 root cause = init Gene saturation) |
| **Q4** | **Reputation gini < 0.6** | **✅ All 500 runs gini ≈ 0.135** | **decay_floor vestigial in [0.01, 0.20]** |

**Meta-finding**: §3.4 stage-3's empirical value is *not* parameter calibration (the original framing). Its real value is **the systematic discovery of a model-realization gap that affects 3 of the 4 questions through a single shared cause** — the current ABM cannot produce concentrated markets, so any parameter targeting concentration has no behavioral expression.

This is a bona-fide protocol-engineering insight, not a failed sweep. Spec §6 (Reputation) and Spec §33 (ESS) are mathematically sound; the gap lives in ABM realization, and E1 is the engineering unlock.

---

## 5. Q4 Acceptance Assessment

| Criterion | Result | Status |
|-----------|--------|--------|
| 100 赛季后基尼 < 0.6 | gini ≈ 0.135 across all 500 runs (22.5% of threshold) | ✅ MET |
| Long-run stability across decay_floor variation | gini constant at 0.135 ± 0.001 spanning 20× decay_floor range | ✅ MET (with caveat: not because the parameter calibrates well, but because it has no effect at all) |

**Q4 status: ✅ ACCEPTED.** Caveat: the reason it passes is the same reason all 5 decay_floor values look identical — the ABM never produces a reputation distribution unbalanced enough for decay_floor to matter.

---

## 6. Recommendations

### Immediate
1. ✅ Document this report in `protocol-v0.9-plan.md` §3.4 Q4 row.
2. ✅ Add §9 decision log entry covering Q4 + joint §3.4 retrospective.
3. ✅ Note in §3.4 that v0.9 stage-3 has surfaced a coherent meta-finding worthy of its own ADR or §3.4 closing summary.

### Deferred (post-E1, v1.0)
4. Re-run Q4 with new ABM dynamics after E1 lands — only then will decay_floor have non-trivial expression.
5. Consider whether spec-recommended decay_floor=0.20 vs current default 0.01 is actually a meaningful choice, or a parameter that should be retired in v1.0+ if E1 still doesn't make it matter.

### Hygiene
6. (Non-blocking) Fix `sweep_q4.yaml`'s `metrics_of_interest` field — current names (`reputation_variance_long_run`, `reputation_floor_violations`, `active_gene_count_long_run`) don't match real ABM output keys, causing summary.json's `per_value` to be empty. The data is fully recoverable from results.csv, but the YAML should reference real keys (`gini`, `HHI`, `shannon_diversity`).

---

## 7. Raw Data

- `results.csv`: 500 rows, 13 columns including the key `gini` for acceptance check
- `summary.json`: present but per_value empty due to metrics_of_interest mismatch (see §6 Hygiene)
- `sweep.log`: stdout (5 progress lines, 3.76h elapsed)

---

## 8. Combined C-R10 + C-R11 + C-R12 Headline (1250 runs)

> **v0.9 §3.4 Stage-3 ABM sweeps (1250 runs across Q1/Q2/Q4) converge on a single empirical insight: alpha and decay_floor are vestigial parameters in the current ABM realization.** Both Q1 acceptance (Nash equilibrium exists, insensitive to seeds) and Q4 acceptance (long-run gini < 0.6) are met, but for a reason none of us anticipated — the model produces a near-uniform distribution that makes both concentration-dampening (alpha) and decay-floor (decay_floor) mechanisms inert. The protocol design (Spec §6, §33) remains mathematically sound. The gap is in ABM realization; E1 (D-04, v1.0 §4.5.X) is the engineering unlock that will give these parameters non-trivial behavioral expression in future re-tests.

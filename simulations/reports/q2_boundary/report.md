# Q2 Boundary — alpha = 0 vs alpha > 0 (C-R11 ABM Sweep Report)

**Simulation run**: 2026-05-19 10:05 → 2026-05-19 10:59 (UTC+8)  
**Duration**: 54 min | **Total runs**: 250 (5 alpha values × 50 runs)  
**Scale**: Tier 1 — n_genes=200, n_developers=50, n_seasons=100  
**Config**: `configs/sweep_q2_boundary.yaml`

---

## 1. Purpose

Close the loop on C-R10 Q1 finding (α ∈ [0.1, 0.9] showed no differential effect on equilibrium HHI). Two competing hypotheses:

- **H1 (switch hypothesis)**: alpha is a discrete switch — α=0 produces WTA dynamics; α>0 produces dispersed equilibrium. Edge between them at α=0.
- **H2 (no-effect hypothesis)**: alpha has no measurable influence on this ABM at Tier-1/Tier-2 scale.

This sweep adds α=0 (closed switch) and α=0.01 (just opened) to test H1.

---

## 2. Results

### 2.1 Core Metrics

| α    | HHI mean ± std    | CI95     | Shannon mean | top10_share | diversity_factor |
|------|-------------------|----------|--------------|-------------|------------------|
| 0.00 | 2.1436 ± 0.0231   | ±0.0064  | 8.4651       | 0.002241    | 1.000000         |
| 0.01 | 2.1423 ± 0.0259   | ±0.0072  | 8.4657       | 0.002239    | 1.000000         |
| 0.10 | 2.1380 ± 0.0312   | ±0.0087  | 8.4677       | 0.002235    | 0.999998         |
| 0.50 | 2.1405 ± 0.0246   | ±0.0068  | 8.4664       | 0.002237    | 0.999989         |
| 0.90 | 2.1447 ± 0.0322   | ±0.0089  | 8.4646       | 0.002242    | 0.999980         |

### 2.2 Pairwise Significance (α=0 baseline)

| Comparison | Δ HHI    | Pooled CI95 | Significant? |
|------------|----------|-------------|--------------|
| 0 vs 0.01  | -0.0014  | ±0.0096     | ❌ NOT significant |
| 0 vs 0.10  | -0.0056  | ±0.0108     | ❌ NOT significant |
| 0 vs 0.50  | -0.0031  | ±0.0094     | ❌ NOT significant |
| 0 vs 0.90  | +0.0011  | ±0.0110     | ❌ NOT significant |

**Result: H1 (switch hypothesis) ❌ FALSIFIED. H2 (no-effect hypothesis) supported.**

---

## 3. Root Cause Analysis

### F1 — `diversity_factor` Never Actually Dampens

The mean `diversity_factor` across 250 runs sits at **≈ 1.000000** for *all* alpha values, including α=0.9. The formula is:

```
diversity_factor = max((1 - normalized_HHI)^alpha, DIVERSITY_FLOOR=0.1)
```

For dampening to be observable, `(1 - normalized_HHI)` needs to be meaningfully < 1, which requires `normalized_HHI` itself to be substantially > 0 (i.e., a concentrated market).

### F2 — Market is Pathologically Dispersed at Tier-1/Tier-2 Scale

`top10_share ≈ 0.22%` across all runs — the entire Top-10 collectively holds about 1/450 of total developer attention. With 200-500 active genes and 50-100 developers issuing constant `install` calls, the share-of-attention distribution is nearly flat.

When the distribution is flat, `normalized_HHI → 0`, and `(1 - 0)^alpha = 1` regardless of alpha. The dampening machinery *exists* in the code but has nothing to dampen.

### F3 — alpha is a "Vestigial Knob" in the Current Model

Combined with C-R10 Q1's Tier-2 finding (α ∈ [0.1, 0.9], 500 runs, no differential effect), the conclusion across **750 total runs** is:

> **alpha is neither a switch nor a knob in the current ABM. It is a vestigial parameter — the formula is wired in but never engages because the market never concentrates.**

This is consistent with — and explains — Spec §33 Theorem 33.1's mathematical claim ("α>0 is sufficient for ESS existence") being correct *in theory*, while having zero behavioral expression *in the current ABM realization*.

---

## 4. Cross-Reference to Earlier Work

### 4.1 Reconsidering C-R8 Q2 "α=0.5 empirical optimum"

The previous Q2 sweep (`reports/q2_diversity/`, commit `67ce8d0`, 2026-05-17) reported α=0.5 as the empirical optimum. With the current 250-run boundary data and combined-with-Q1 750-run picture, that conclusion appears to be a textbook **M10 spurious-precision** instance:

- C-R8 Q2 5-α HHI range: 2.138 ~ 2.150 (Δ ≈ 0.012)
- Within-α std: 0.024 ~ 0.033 (≈ 2-3× the cross-α range)
- Differences between α values are inside the noise floor

**Recommendation**: amend C-R8 Q2 narrative to acknowledge the apparent ranking is below the noise floor; α=0.5 should be retained as a *protocol default*, not as an *empirical optimum*. (Logged as Q2-followup item; non-blocking.)

### 4.2 Why D-04 / E1 Becomes the Unblocking Path

For alpha to ever matter in ABM, the market needs to actually concentrate. The current ABM cannot produce concentration because of the structural bug surfaced by R9 (init genes permanently saturate Top-10, but new genes never enter — yet the Top-10 itself is a thin slice). E1 (newcomer_bonus → Arena selection, deferred to v1.0 §4.5.X per D-04) is a prerequisite for any future re-test of alpha effect: only when the Top-10 holds a meaningful share *and* genes circulate through it can `(1 - normalized_HHI)^alpha` express its design intent.

---

## 5. Q2 Acceptance Assessment (Original Plan)

| Criterion | Result | Status |
|-----------|--------|--------|
| HHI 显著低于无 diversity_factor 的对照组 | α=0 (no diversity_factor) vs α=0.5: ΔHHI=-0.0031, NOT significant | ❌ NOT MET |

**Q2 status: ❌ FALSIFIED at Tier-1 scale. Re-test deferred until E1 lands in v1.0.**

This is *not* a bug in the protocol design — Spec §33 Theorem 33.1 is mathematically sound. It is a **model-realization gap**: the current ABM cannot generate the conditions under which the diversity_factor mechanism operates.

---

## 6. Findings Summary

| Finding | Status |
|---------|--------|
| **F1** — `diversity_factor` ≡ 1 across all alpha values | Empirical, 250 runs |
| **F2** — Market is pathologically dispersed (top10_share ≈ 0.22%) | Empirical |
| **F3** — alpha is vestigial in current ABM (combined Q1+Q2: 750 runs, all NS) | Empirical conclusion |
| **F4** — C-R8 Q2 "α=0.5 optimum" claim is spurious-precision (M10) | Cross-reference |
| **F5** — E1 (D-04) is prerequisite for any future alpha re-test | Routing decision |

---

## 7. Recommendations

### Immediate
1. ✅ Document this report and link from `protocol-v0.9-plan.md` §3.4 Q2 row.
2. ✅ Add §9 decision log entry: Q2 falsified at Tier-1; alpha is vestigial.

### Deferred (V1.0)
3. After E1 (newcomer_bonus → Arena) lands and produces a non-trivial top10_share, re-run a Q2-equivalent sweep at the new model state.
4. Consider whether `diversity_factor` should also be tested *post-E1* to validate the protocol design end-to-end (closing the "Spec → ABM" loop properly).

### Documentation Hygiene
5. (Non-blocking) Annotate C-R8 Q2 (`reports/q2_diversity/report.md`) with a note pointing to this report's F4 finding.

---

## 8. Raw Data

- `results.csv`: 250 rows (one per run)
- `summary.json`: per-α mean/std/CI95
- `sweep.log`: stdout from sweep_runner

---

## 9. Combined C-R10 + C-R11 Headline (for plan §9 entry)

> Across 750 ABM runs spanning α ∈ {0, 0.01, 0.1, 0.3, 0.5, 0.7, 0.9} at both Tier-1 (50 runs/α) and Tier-2 (100 runs/α) scales, the diversity_factor parameter shows no measurable behavioral effect. The mechanism is correctly implemented in code but does not engage because the ABM market is structurally too dispersed to invoke the dampening formula. This identifies E1 (D-04, v1.0 §4.5.X) as a prerequisite for any future protocol-empirical validation of Spec §33 ESS dynamics.

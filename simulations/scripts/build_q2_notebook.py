"""Generate notebooks/q2_diversity_factor.ipynb from a template.

Stage-3 R8 helper. Run once after the Q2 sweep completes (or with --skeleton
to write a skeleton notebook before the sweep finishes — useful for parallel
authoring of the report and the notebook).

Usage:
    python scripts/build_q2_notebook.py
    python scripts/build_q2_notebook.py --skeleton  # placeholder before sweep done
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "q2_diversity_factor.ipynb"


MARKDOWN_HEADER = """\
# Q2 — diversity_factor (α) effectiveness

This notebook renders the Q2 sweep results — see
[`reports/q2_diversity/report.md`](../reports/q2_diversity/report.md) for the
written analysis and [`configs/sweep_q2.yaml`](../configs/sweep_q2.yaml) for
the sweep configuration.

**Acceptance criterion** (Rotifer Protocol v0.9 plan §3.4): HHI significantly
lower than no-diversity_factor control. Variants tested: α ∈ {0.1, 0.3, 0.5,
0.7, 0.9} × 50 runs each.

Run order:

1. Load `reports/q2_diversity/results.csv` + `summary.json`
2. Plot HHI / Shannon / Top10 share vs α with 95% CI error bars
3. Print recommended α range (latest summary)
"""


CODE_LOAD = """\
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
REPORT_DIR = PROJECT_ROOT / "reports" / "q2_diversity"

results = pd.read_csv(REPORT_DIR / "results.csv")
with (REPORT_DIR / "summary.json").open() as fh:
    summary = json.load(fh)

print(f"Loaded {len(results)} rows · α values = {sorted(results['alpha'].unique())}")
results.head()
"""


CODE_HHI = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("alpha").agg(
    HHI_mean=("HHI", "mean"),
    HHI_std=("HHI", "std"),
    n=("HHI", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["HHI_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["alpha"], agg["HHI_mean"], yerr=agg["ci95"],
            fmt="o-", color="steelblue", capsize=4, label="HHI mean ± 95% CI")
ax.set_xlabel("α (diversity_factor exponent)")
ax.set_ylabel("HHI (concentration index, scaled to 10000)")
ax.set_title("Q2 — HHI vs α  (Tier 1: 200 Genes × 50 runs × 100 seasons)")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_hhi_vs_alpha.png", dpi=120)
plt.show()
agg
"""


CODE_SHANNON = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("alpha").agg(
    H_mean=("shannon_diversity", "mean"),
    H_std=("shannon_diversity", "std"),
    n=("shannon_diversity", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["H_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["alpha"], agg["H_mean"], yerr=agg["ci95"],
            fmt="s-", color="darkorange", capsize=4,
            label="Shannon mean ± 95% CI")
ax.set_xlabel("α (diversity_factor exponent)")
ax.set_ylabel("Shannon entropy")
ax.set_title("Q2 — Shannon diversity vs α")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_shannon_vs_alpha.png", dpi=120)
plt.show()
agg
"""


CODE_TOP10 = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("alpha").agg(
    T_mean=("top10_share", "mean"),
    T_std=("top10_share", "std"),
    n=("top10_share", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["T_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["alpha"], agg["T_mean"], yerr=agg["ci95"],
            fmt="^-", color="seagreen", capsize=4,
            label="Top-10 share mean ± 95% CI")
ax.set_xlabel("α (diversity_factor exponent)")
ax.set_ylabel("Top-10 Gene fitness share (fraction)")
ax.set_title("Q2 — Top-10 share vs α")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_top10_share_vs_alpha.png", dpi=120)
plt.show()
agg
"""


MARKDOWN_FINDINGS = """\
## Findings (auto-update after each sweep run)

The plots above feed directly into the report's §3 tables and §4 narrative.
Recommendation logic implemented in `reports/q2_diversity/report.md` §4.3:

1. If HHI(α=0.1) and HHI(α=0.9) **95% CI overlaps** at the chosen Tier-1 horizon,
   the spec-recommended α=0.3 vs plan-default α=0.5 is **not statistically
   distinguishable** under display-layer-only routing — log this in §6 as a
   prerequisite for the Arena-layer α experiment.
2. If they don't overlap, fit a smoothed curve and pick α at the inflection
   point as the recommended `seasons.config.diversity_factor_alpha`.

(See `reports/q2_diversity/report.md` for the written rendering.)
"""


def build_notebook() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell(MARKDOWN_HEADER),
        nbformat.v4.new_code_cell(CODE_LOAD),
        nbformat.v4.new_code_cell(CODE_HHI),
        nbformat.v4.new_code_cell(CODE_SHANNON),
        nbformat.v4.new_code_cell(CODE_TOP10),
        nbformat.v4.new_markdown_cell(MARKDOWN_FINDINGS),
    ]
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3 (rotifer-simulations)",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {"name": "python"}
    return nb


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Q2 notebook")
    parser.add_argument(
        "--skeleton",
        action="store_true",
        help="Write notebook skeleton without sweep data (cells unexecuted)",
    )
    args = parser.parse_args(argv)
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"[notebook] wrote → {NOTEBOOK_PATH}")
    if not args.skeleton:
        print(
            "[notebook] cells are unexecuted; run interactively with jupyter "
            "or use papermill to execute against the latest sweep CSV."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

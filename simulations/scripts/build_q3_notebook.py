"""Generate notebooks/q3_season_length.ipynb from a template.

Stage-3 R9 helper. Usage mirrors ``build_q2_notebook.py``:

    python scripts/build_q3_notebook.py
    python scripts/build_q3_notebook.py --skeleton

Run order (after the sweep finishes):

    1. python -m src.sweep_runner --config configs/sweep_q3.yaml
    2. python scripts/build_q3_notebook.py
    3. python -c "import nbclient, nbformat; ..."  (executes the notebook;
       see Q2's pattern in scripts/build_q2_notebook.py)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import nbformat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "q3_season_length.ipynb"


MARKDOWN_HEADER = """\
# Q3 — Season length and newcomer entry rate

This notebook renders the Q3 sweep results — see
[`reports/q3_season_length/report.md`](../reports/q3_season_length/report.md)
for the written analysis and [`configs/sweep_q3.yaml`](../configs/sweep_q3.yaml)
for the sweep configuration.

**Acceptance criterion** (Rotifer Protocol v0.9 plan §3.4): newcomer entry
rate into Top-10 > 20%. Variants tested: season length ∈ {30, 60, 90, 120,
180} days × 50 runs each, plan default = 90 days (per Spec §24.4 recommendation).

**Note on metric semantics**:
- `top10_newcomer_rate` — fraction of Top-10 Genes whose author age ≤ 30 days
  (the newcomer protection window; per `top_n_newcomer_rate` in metrics.py).
- `average_first_publish_to_top10_days` — current Top-10 mean age in days
  (`mean(now_step − first_publish_step) × DAYS_PER_STEP=3`). This is a
  **proxy** for "Gene first publish → first reach Top-10" trajectory; the
  precise trajectory metric needs per-step ranking history (deferred to
  stage 4). The proxy is monotonic in season length so it preserves the
  qualitative Q3 signal.
- `gini` — fitness inequality across all Genes (0 = equal, 1 = single
  dominant Gene).

Run order:

1. Load `reports/q3_season_length/results.csv` + `summary.json`
2. Plot the three primary metrics vs season length with 95% CI error bars
3. Print recommended season length range
"""


CODE_LOAD = """\
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
REPORT_DIR = PROJECT_ROOT / "reports" / "q3_season_length"

results = pd.read_csv(REPORT_DIR / "results.csv")
with (REPORT_DIR / "summary.json").open() as fh:
    summary = json.load(fh)

print(f"Loaded {len(results)} rows · season lengths = "
      f"{sorted(results['season_length_days'].unique())}")
results.head()
"""


CODE_NEWCOMER = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("season_length_days").agg(
    newcomer_mean=("top10_newcomer_rate", "mean"),
    newcomer_std=("top10_newcomer_rate", "std"),
    n=("top10_newcomer_rate", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["newcomer_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["season_length_days"], agg["newcomer_mean"], yerr=agg["ci95"],
            fmt="o-", color="seagreen", capsize=4,
            label="Top-10 newcomer rate ± 95% CI")
ax.axhline(0.20, color="crimson", linestyle="--", alpha=0.6,
           label="acceptance: > 0.20 (plan §3.4)")
ax.set_xlabel("Season length (days)")
ax.set_ylabel("Top-10 newcomer rate (fraction)")
ax.set_title(
    "Q3 — Top-10 newcomer rate vs season length\\n"
    "(Tier 1: 200 Genes × 50 runs × 100 seasons)"
)
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_newcomer_rate_vs_season_length.png", dpi=120)
plt.show()
agg
"""


CODE_AGE = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("season_length_days").agg(
    age_mean=("average_first_publish_to_top10_days", "mean"),
    age_std=("average_first_publish_to_top10_days", "std"),
    n=("average_first_publish_to_top10_days", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["age_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["season_length_days"], agg["age_mean"], yerr=agg["ci95"],
            fmt="s-", color="darkorange", capsize=4,
            label="Top-10 mean age (days) ± 95% CI")
ax.set_xlabel("Season length (days)")
ax.set_ylabel("Top-10 mean age (days)")
ax.set_title(
    "Q3 — Top-10 mean age (proxy for first-publish→Top-10 trajectory)\\n"
    "Linear-in-season-length proxy; full trajectory metric is stage-4 work"
)
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_top10_age_vs_season_length.png", dpi=120)
plt.show()
agg
"""


CODE_GINI = """\
fig, ax = plt.subplots(figsize=(8, 5))
agg = results.groupby("season_length_days").agg(
    gini_mean=("gini", "mean"),
    gini_std=("gini", "std"),
    n=("gini", "count"),
).reset_index()
agg["ci95"] = 1.96 * agg["gini_std"] / agg["n"].pow(0.5)

ax.errorbar(agg["season_length_days"], agg["gini_mean"], yerr=agg["ci95"],
            fmt="^-", color="steelblue", capsize=4,
            label="Gini coefficient ± 95% CI")
ax.set_xlabel("Season length (days)")
ax.set_ylabel("Gini coefficient (fitness inequality)")
ax.set_title("Q3 — Fitness Gini vs season length")
ax.grid(True, alpha=0.3)
ax.legend()
plt.tight_layout()
plt.savefig(REPORT_DIR / "fig_gini_vs_season_length.png", dpi=120)
plt.show()
agg
"""


MARKDOWN_FINDINGS = """\
## Findings (auto-update after each sweep run)

The plots above feed directly into the report's §3 tables and §4 narrative.
Recommendation logic implemented in `reports/q3_season_length/report.md` §4.3.

Key Q3 questions:

1. **Does the plan default 90 days satisfy newcomer rate > 0.20?**
   See `fig_newcomer_rate_vs_season_length.png` — the 0.20 acceptance
   threshold is rendered as a dashed crimson line. Inspect whether 90 days
   sits above the line at 95% CI.

2. **Is there a monotonic relationship between season length and newcomer
   rate?** Shorter seasons → more frequent F(g) half-life resets → newer
   Genes have more chance to enter Top-10. The plot direction validates
   or refutes this expectation.

3. **Does Top-10 mean age scale linearly with season length?** As a sanity
   check on the proxy metric — yes implies "longer season = older Top-10",
   confirming the qualitative direction even if the proxy isn't a direct
   trajectory measurement.

(See `reports/q3_season_length/report.md` for the written rendering.)
"""


def build_notebook() -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    nb.cells = [
        nbformat.v4.new_markdown_cell(MARKDOWN_HEADER),
        nbformat.v4.new_code_cell(CODE_LOAD),
        nbformat.v4.new_code_cell(CODE_NEWCOMER),
        nbformat.v4.new_code_cell(CODE_AGE),
        nbformat.v4.new_code_cell(CODE_GINI),
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
    parser = argparse.ArgumentParser(description="Generate Q3 notebook")
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
            "or use nbclient to execute against the latest sweep CSV."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

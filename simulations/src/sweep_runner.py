"""Sweep runner — execute a single-axis parameter sweep for an ABM config.

Stage-3 R8: drives Q1-Q4 sweeps from the ``configs/sweep_*.yaml`` files
that were laid out in stage-2 (the YAMLs are real but the runner that
consumes them was deferred to stage-3 per plan §3.4).

Usage:
    python -m src.sweep_runner --config configs/sweep_q2.yaml
    python -m src.sweep_runner --config configs/sweep_q2.yaml --dry-run
    python -m src.sweep_runner --config configs/sweep_q2.yaml --limit-runs 5

Output (relative to project root):
    {output_dir}/results.csv      — one row per (sweep_value, run_idx)
    {output_dir}/summary.json     — per-value mean / std / 95% CI

Determinism:
    seed_per_run = base_seed + sweep_value_idx * 1000 + run_idx
    Verified by tests/test_sweep_runner.py (C.10.1–C.10.3).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Sequence

from .model import DAYS_PER_STEP, ModelConfig, RotiferModel, load_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def override_config(config: ModelConfig, parameter: str, value: Any) -> ModelConfig:
    """Apply a single-axis parameter override to a ``ModelConfig`` clone.

    Only top-level scalar fields are supported in stage-3 R8. Nested keys
    (e.g. ``developer_strategy_mix.carr`` for Q2.5) will land in C-R12 with
    an explicit dotted-path resolver — kept out of this module to honour
    rotifer-test-discipline §5.4 (no overfit: today's caller does not need
    the dotted-path machinery, so we don't ship it speculatively).

    Special case (R9): ``season_length_days`` also re-derives
    ``n_steps_per_season`` so the simulation clock stays consistent with
    the human-friendly knob. Without this the model would still tick at
    the baseline 30 steps even when the YAML asks for a 30-day or 180-day
    season — silent drift between intent and behaviour.
    """
    if not hasattr(config, parameter):
        raise ValueError(
            f"Sweep parameter {parameter!r} has no matching ModelConfig field. "
            "Either rename the YAML 'parameter:' to a real ModelConfig attribute "
            "or extend override_config to handle nested keys."
        )
    if parameter == "season_length_days":
        new_steps = max(1, round(int(value) / DAYS_PER_STEP))
        return replace(
            config,
            season_length_days=int(value),
            n_steps_per_season=new_steps,
        )
    return replace(config, **{parameter: value})


def run_single(config: ModelConfig, *, seed: int) -> dict[str, Any]:
    """Run a single ``RotiferModel`` with overridden seed → final metrics."""
    cfg = replace(config, seed=seed)
    model = RotiferModel(cfg)
    return model.run()


def aggregate(
    rows: Sequence[dict[str, Any]],
    metric_keys: Sequence[str],
) -> dict[str, dict[str, float]]:
    """Per-metric mean / std / 95% CI for the given rows.

    Empty rows ⇒ empty dict (caller decides whether to error). Metrics not
    present in every row are skipped per-row (graceful — keeps mixed-emit
    runs robust).
    """
    out: dict[str, dict[str, float]] = {}
    if not rows:
        return out
    for metric in metric_keys:
        values = [r[metric] for r in rows if metric in r]
        if not values:
            continue
        n = len(values)
        mean = sum(values) / n
        if n == 1:
            std = 0.0
            ci95 = 0.0
        else:
            var = sum((v - mean) ** 2 for v in values) / (n - 1)
            std = math.sqrt(var)
            ci95 = 1.96 * std / math.sqrt(n)
        out[metric] = {"mean": mean, "std": std, "ci95": ci95, "n": float(n)}
    return out


def execute_sweep(
    config_path: Path,
    *,
    dry_run: bool = False,
    limit_runs: int | None = None,
    write_outputs: bool = True,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    """Run one sweep YAML end-to-end. Returns a manifest dict.

    Manifest fields:
        config, parameter, values, n_runs_per_param, base_seed,
        metric_keys, rows (list of dict), summary (per-value aggregate),
        elapsed_seconds.

    The ``write_outputs=False`` path is for tests — they want the manifest
    in-memory without polluting reports/.
    """
    base_config = load_config(config_path)
    raw = base_config.raw
    sweep = raw.get("sweep", {})
    parameter = sweep.get("parameter")
    values = sweep.get("values", [])
    if not parameter or not values:
        raise ValueError(
            f"Sweep config {config_path} missing sweep.parameter / sweep.values"
        )

    n_runs_yaml = int(raw.get("n_runs_per_param", 50))
    n_runs = 1 if dry_run else n_runs_yaml
    if limit_runs is not None:
        n_runs = min(n_runs, limit_runs)

    output_dir_raw = raw.get("output_dir", f"reports/sweep-{parameter}/")
    output_dir = Path(output_dir_raw)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir
    if write_outputs:
        output_dir.mkdir(parents=True, exist_ok=True)

    metric_keys = list(
        raw.get("metrics_of_interest", ["HHI", "shannon_diversity", "top10_share"])
    )

    base_seed = base_config.seed
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()

    print(
        f"[sweep] {parameter}: {values} × {n_runs} runs"
        f" (output → {output_dir if write_outputs else '(in-memory)'})",
        flush=True,
    )

    for sweep_idx, value in enumerate(values):
        cfg_for_value = override_config(base_config, parameter, value)
        for run_idx in range(n_runs):
            seed = base_seed + sweep_idx * 1000 + run_idx
            metrics = run_single(cfg_for_value, seed=seed)
            row: dict[str, Any] = {
                parameter: value,
                "run_idx": run_idx,
                "seed": seed,
            }
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    row[k] = float(v)
            rows.append(row)
        print(
            f"[sweep] {parameter}={value}: {n_runs} runs done"
            f" (elapsed {time.perf_counter() - t0:.1f}s)",
            flush=True,
        )

    elapsed = time.perf_counter() - t0
    summary_per_value: dict[str, dict[str, dict[str, float]]] = {}
    for value in values:
        rows_v = [r for r in rows if r[parameter] == value]
        summary_per_value[str(value)] = aggregate(rows_v, metric_keys)

    summary = {
        "config": str(config_path.resolve().relative_to(project_root.resolve())),
        "parameter": parameter,
        "values": values,
        "n_runs_per_param": n_runs,
        "base_seed": base_seed,
        "metric_keys": metric_keys,
        "per_value": summary_per_value,
        "elapsed_seconds": elapsed,
    }

    if write_outputs:
        _write_results_csv(output_dir / "results.csv", rows)
        _write_summary_json(output_dir / "summary.json", summary)
        print(
            f"[sweep] wrote {len(rows)} rows → {output_dir / 'results.csv'}",
            flush=True,
        )
        print(
            f"[sweep] wrote summary → {output_dir / 'summary.json'}",
            flush=True,
        )

    manifest = dict(summary)
    manifest["rows"] = rows
    return manifest


def _write_results_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_summary_json(path: Path, summary: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run an ABM parameter sweep")
    parser.add_argument("--config", required=True, help="Path to sweep YAML")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="One run per sweep value (smoke / pipeline check)",
    )
    parser.add_argument(
        "--limit-runs",
        type=int,
        default=None,
        help="Cap runs per sweep value (default: read from YAML n_runs_per_param)",
    )
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = PROJECT_ROOT / config_path

    if not config_path.exists():
        print(f"[sweep] config not found: {config_path}", file=sys.stderr)
        return 2

    execute_sweep(
        config_path,
        dry_run=args.dry_run,
        limit_runs=args.limit_runs,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

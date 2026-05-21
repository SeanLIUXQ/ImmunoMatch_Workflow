from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from run_immunomatch_toy import run_immunomatch_batches_local

from .batch_engine import ImprovedImmunoMatchScorer
from .metrics import choose_threshold_by_accuracy, summarize_scores
from .pair_builder import build_repeated_benchmark_pairs
from .visuals import save_comparison_figure


def add_common_score_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", required=True, help="Input CSV with VH, VL and light-chain type columns.")
    parser.add_argument("--output", required=True, help="Output scored CSV path.")
    parser.add_argument("--model-root", default="models", help="Directory containing immunomatch-kappa and immunomatch-lambda.")
    parser.add_argument("--hseq-col", default="VH")
    parser.add_argument("--lseq-col", default="VL")
    parser.add_argument("--ltype-col", default="locus", help="Light-chain type column, usually locus or light_chain_type.")


def command_baseline(args: argparse.Namespace) -> None:
    data = pd.read_csv(args.input)
    input_data = data.rename(columns={args.ltype_col: "light_chain_type"}) if args.ltype_col != "light_chain_type" else data
    start = time.perf_counter()
    scored = run_immunomatch_batches_local(
        input_data,
        hseq_col=args.hseq_col,
        lseq_col=args.lseq_col,
        ltype_col="light_chain_type",
        model_root=Path(args.model_root),
    )
    elapsed = time.perf_counter() - start
    if args.ltype_col != "light_chain_type":
        scored = scored.rename(columns={"light_chain_type": args.ltype_col})
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.output, index=False)
    print(json.dumps({"method": "baseline", "rows": int(len(scored)), "runtime_sec": elapsed, "output": args.output}, indent=2))


def command_improved(args: argparse.Namespace) -> None:
    data = pd.read_csv(args.input)
    start = time.perf_counter()
    scorer = ImprovedImmunoMatchScorer(model_root=Path(args.model_root))
    scored = scorer.score_dataframe(data, hseq_col=args.hseq_col, lseq_col=args.lseq_col, locus_col=args.ltype_col)
    elapsed = time.perf_counter() - start
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(args.output, index=False)
    print(json.dumps({"method": "improved", "rows": int(len(scored)), "runtime_sec": elapsed, "output": args.output}, indent=2))


def command_benchmark(args: argparse.Namespace) -> None:
    source = pd.read_csv(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    benchmark = build_repeated_benchmark_pairs(source, n_pairs=args.n_pairs, seed=args.seed, repeats=args.repeats)
    benchmark.to_csv(output_dir / "benchmark_pairs.csv", index=False)

    baseline_input = benchmark.rename(columns={"locus": "light_chain_type"})
    start = time.perf_counter()
    baseline_scored = run_immunomatch_batches_local(
        baseline_input,
        hseq_col="VH",
        lseq_col="VL",
        ltype_col="light_chain_type",
        model_root=Path(args.model_root),
    ).rename(columns={"light_chain_type": "locus"})
    baseline_time = time.perf_counter() - start
    baseline_scored.to_csv(output_dir / "original_scored.csv", index=False)

    scorer = ImprovedImmunoMatchScorer(model_root=Path(args.model_root))
    start = time.perf_counter()
    improved_scored = scorer.score_dataframe(benchmark, hseq_col="VH", lseq_col="VL", locus_col="locus")
    improved_time = time.perf_counter() - start
    improved_scored.to_csv(output_dir / "improved_scored.csv", index=False)

    train_idx, test_idx = train_test_split(
        benchmark.index,
        test_size=0.5,
        random_state=args.seed,
        stratify=benchmark["label"],
    )
    threshold, _ = choose_threshold_by_accuracy(
        improved_scored.loc[train_idx, "label"],
        improved_scored.loc[train_idx, "pairing_scores"],
    )
    baseline_metrics = summarize_scores(
        baseline_scored.loc[test_idx, "label"],
        baseline_scored.loc[test_idx, "pairing_scores"],
        threshold=0.5,
    )
    improved_metrics = summarize_scores(
        improved_scored.loc[test_idx, "label"],
        improved_scored.loc[test_idx, "pairing_scores"],
        threshold=threshold,
    )
    baseline_metrics["runtime_sec"] = float(baseline_time)
    improved_metrics["runtime_sec"] = float(improved_time)
    baseline_metrics["speedup_vs_original"] = 1.0
    improved_metrics["speedup_vs_original"] = float(baseline_time / improved_time) if improved_time else float("inf")
    payload = {
        "benchmark_settings": {
            "n_pairs": args.n_pairs,
            "repeats": args.repeats,
            "n_rows": int(len(benchmark)),
            "unique_pairs": int(benchmark[["VH", "VL", "locus"]].drop_duplicates().shape[0]),
            "seed": args.seed,
        },
        "original": baseline_metrics,
        "improved": improved_metrics,
    }
    (output_dir / "benchmark_metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    save_comparison_figure(baseline_metrics, improved_metrics, output_dir)
    print(json.dumps(payload, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for the ImmunoMatch lightweight and improved workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    baseline = subparsers.add_parser("baseline", help="Run the original local wrapper.")
    add_common_score_args(baseline)
    baseline.set_defaults(func=command_baseline)

    improved = subparsers.add_parser("improved", help="Run the improved cached scorer.")
    add_common_score_args(improved)
    improved.set_defaults(func=command_improved)

    benchmark = subparsers.add_parser("benchmark", help="Benchmark original vs improved workflows.")
    benchmark.add_argument("--input", default="example_input/King_Tonsil_GC_paired.csv")
    benchmark.add_argument("--model-root", default="models")
    benchmark.add_argument("--output-dir", default="benchmark_results")
    benchmark.add_argument("--n-pairs", type=int, default=24)
    benchmark.add_argument("--repeats", type=int, default=4)
    benchmark.add_argument("--seed", type=int, default=13)
    benchmark.set_defaults(func=command_benchmark)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()

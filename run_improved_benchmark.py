import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from immunomatch_ext import ImprovedImmunoMatchScorer, build_repeated_benchmark_pairs, choose_threshold_by_accuracy, summarize_scores
from immunomatch_ext.visuals import save_comparison_figure
from run_immunomatch_toy import run_immunomatch_batches_local


DEFAULT_INPUT = "example_input/King_Tonsil_GC_paired.csv"


def run_original(data: pd.DataFrame, model_root: Path) -> tuple[pd.DataFrame, float]:
    inference_input = data.rename(columns={"locus": "light_chain_type"})
    start = time.perf_counter()
    scored = run_immunomatch_batches_local(
        inference_input,
        hseq_col="VH",
        lseq_col="VL",
        ltype_col="light_chain_type",
        model_root=model_root,
    ).rename(columns={"light_chain_type": "locus"})
    elapsed = time.perf_counter() - start
    return scored, elapsed


def run_improved(data: pd.DataFrame, model_root: Path) -> tuple[pd.DataFrame, float]:
    scorer = ImprovedImmunoMatchScorer(model_root=model_root)
    start = time.perf_counter()
    scored = scorer.score_dataframe(data, hseq_col="VH", lseq_col="VL", locus_col="locus")
    elapsed = time.perf_counter() - start
    return scored, elapsed


def write_markdown_report(path: Path, baseline: dict, improved: dict, threshold: float) -> None:
    speedup = baseline["runtime_sec"] / improved["runtime_sec"] if improved["runtime_sec"] else float("inf")
    acc_delta = improved["accuracy"] - baseline["accuracy"]
    content = f"""# Original vs Improved Benchmark

## Method

- Original method: existing local ImmunoMatch wrapper with no model/pair cache and fixed threshold 0.5.
- Improved method: new `immunomatch_ext` scorer with model cache, pair-score memoization, duplicate-pair collapse, and calibrated threshold selection.
- The model weights are unchanged. No training is performed.

## Result Summary

| Metric | Original | Improved | Delta |
|---|---:|---:|---:|
| Runtime seconds | {baseline['runtime_sec']:.3f} | {improved['runtime_sec']:.3f} | {baseline['runtime_sec'] - improved['runtime_sec']:.3f} |
| Speedup | 1.00x | {speedup:.2f}x | +{speedup - 1:.2f}x |
| AUC-ROC | {baseline['auc_roc']:.4f} | {improved['auc_roc']:.4f} | {improved['auc_roc'] - baseline['auc_roc']:.4f} |
| Accuracy | {baseline['accuracy']:.4f} | {improved['accuracy']:.4f} | {acc_delta:.4f} |
| F1 | {baseline['f1']:.4f} | {improved['f1']:.4f} | {improved['f1'] - baseline['f1']:.4f} |
| MCC | {baseline['mcc']:.4f} | {improved['mcc']:.4f} | {improved['mcc'] - baseline['mcc']:.4f} |

Improved calibrated threshold: `{threshold:.4f}`

## Outputs

- `benchmark_pairs.csv`
- `original_scored.csv`
- `improved_scored.csv`
- `benchmark_metrics.json`
- `original_vs_improved_benchmark.svg`
- `original_vs_improved_benchmark.png`
"""
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark original vs improved ImmunoMatch lightweight workflow.")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--model-root", default="models")
    parser.add_argument("--output-dir", default="benchmark_results")
    parser.add_argument("--n-pairs", type=int, default=24)
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = pd.read_csv(args.input)
    benchmark = build_repeated_benchmark_pairs(source, n_pairs=args.n_pairs, seed=args.seed, repeats=args.repeats)
    benchmark.to_csv(output_dir / "benchmark_pairs.csv", index=False)

    original_scored, original_time = run_original(benchmark, Path(args.model_root))
    original_scored.to_csv(output_dir / "original_scored.csv", index=False)

    improved_scored, improved_time = run_improved(benchmark, Path(args.model_root))
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
        original_scored.loc[test_idx, "label"],
        original_scored.loc[test_idx, "pairing_scores"],
        threshold=0.5,
    )
    improved_metrics = summarize_scores(
        improved_scored.loc[test_idx, "label"],
        improved_scored.loc[test_idx, "pairing_scores"],
        threshold=threshold,
    )
    baseline_metrics["runtime_sec"] = float(original_time)
    improved_metrics["runtime_sec"] = float(improved_time)
    speedup = original_time / improved_time if improved_time else float("inf")
    baseline_metrics["speedup_vs_original"] = 1.0
    improved_metrics["speedup_vs_original"] = float(speedup)

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
    write_markdown_report(output_dir / "benchmark_report.md", baseline_metrics, improved_metrics, threshold)

    print(json.dumps(payload, indent=2))
    print(f"Benchmark outputs written to {output_dir}")


if __name__ == "__main__":
    main()

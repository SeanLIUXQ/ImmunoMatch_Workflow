import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve

from run_immunomatch_toy import run_immunomatch_batches_local


DEFAULT_INPUT = "example_input/King_Tonsil_GC_paired.csv"


def make_lightweight_dataset(data: pd.DataFrame, n_pairs: int, seed: int) -> pd.DataFrame:
    required = {"sample_name", "barcode", "VH", "VL", "locus"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Input is missing required columns: {sorted(missing)}")

    clean = data.dropna(subset=["VH", "VL", "locus"]).copy()
    clean = clean[clean["locus"].isin(["IGK", "IGL"])]
    clean = clean.drop_duplicates(subset=["VH", "VL", "locus"])
    if len(clean) < n_pairs:
        raise ValueError(f"Requested {n_pairs} pairs but only {len(clean)} clean pairs are available")

    positives = clean.sample(n=n_pairs, random_state=seed).reset_index(drop=True)
    positives["pair_source"] = "observed_single_cell_pair"
    positives["label"] = 1
    positives["pair_id"] = [f"pos_{i:04d}" for i in range(len(positives))]

    rng = np.random.default_rng(seed)
    negatives = positives.copy()
    shuffled = negatives["VL"].to_numpy().copy()
    shuffled_locus = negatives["locus"].to_numpy().copy()
    for _ in range(200):
        order = rng.permutation(len(negatives))
        if np.all(order != np.arange(len(negatives))):
            shuffled = shuffled[order]
            shuffled_locus = shuffled_locus[order]
            break
    else:
        order = np.roll(np.arange(len(negatives)), 1)
        shuffled = shuffled[order]
        shuffled_locus = shuffled_locus[order]

    negatives["VL"] = shuffled
    negatives["locus"] = shuffled_locus
    negatives["pair_source"] = "shuffled_pseudo_negative"
    negatives["label"] = 0
    negatives["pair_id"] = [f"neg_{i:04d}" for i in range(len(negatives))]

    workflow = pd.concat([positives, negatives], ignore_index=True)
    workflow = workflow.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return workflow[["pair_id", "sample_name", "barcode", "VH", "VL", "locus", "pair_source", "label"]]


def plot_outputs(scored: pd.DataFrame, output_dir: Path) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams.update({"axes.spines.right": False, "axes.spines.top": False, "legend.frameon": False})

    fig, ax = plt.subplots(figsize=(4.4, 3.4))
    groups = [("observed", scored.loc[scored["label"] == 1, "pairing_scores"]), ("shuffled", scored.loc[scored["label"] == 0, "pairing_scores"])]
    ax.boxplot([g[1] for g in groups], tick_labels=[g[0] for g in groups], widths=0.45, showfliers=False)
    rng = np.random.default_rng(7)
    for idx, (_, values) in enumerate(groups, start=1):
        x = rng.normal(idx, 0.035, size=len(values))
        ax.scatter(x, values, s=12, alpha=0.55)
    ax.axhline(0.5, color="0.55", linestyle="--", linewidth=1)
    ax.set_ylabel("ImmunoMatch pairing score")
    ax.set_xlabel("Pair construction")
    fig.tight_layout()
    fig.savefig(output_dir / "score_distribution.svg", bbox_inches="tight")
    fig.savefig(output_dir / "score_distribution.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

    fpr, tpr, _ = roc_curve(scored["label"], scored["pairing_scores"])
    auc = roc_auc_score(scored["label"], scored["pairing_scores"])
    fig, ax = plt.subplots(figsize=(3.6, 3.4))
    ax.plot(fpr, tpr, color="#0F4D92", linewidth=2, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], color="0.6", linestyle="--", linewidth=1)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output_dir / "roc_curve.svg", bbox_inches="tight")
    fig.savefig(output_dir / "roc_curve.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a lightweight paper-style ImmunoMatch workflow.")
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--model-root", default="models")
    parser.add_argument("--output-dir", default="lightweight_paper_workflow")
    parser.add_argument("--n-pairs", type=int, default=24)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    source = pd.read_csv(args.input)
    dataset = make_lightweight_dataset(source, n_pairs=args.n_pairs, seed=args.seed)
    dataset_path = output_dir / "lightweight_pairs.csv"
    dataset.to_csv(dataset_path, index=False)

    inference_input = dataset.rename(columns={"locus": "light_chain_type"})
    scored = run_immunomatch_batches_local(
        inference_input,
        hseq_col="VH",
        lseq_col="VL",
        ltype_col="light_chain_type",
        model_root=Path(args.model_root),
    ).rename(columns={"light_chain_type": "locus"})

    scored_path = output_dir / "lightweight_pairs_scored.csv"
    scored.to_csv(scored_path, index=False)

    predicted = (scored["pairing_scores"] >= 0.5).astype(int)
    metrics = {
        "n_positive": int((scored["label"] == 1).sum()),
        "n_pseudo_negative": int((scored["label"] == 0).sum()),
        "auc_roc": float(roc_auc_score(scored["label"], scored["pairing_scores"])),
        "accuracy_at_0.5": float(accuracy_score(scored["label"], predicted)),
        "confusion_matrix_at_0.5": confusion_matrix(scored["label"], predicted).tolist(),
        "mean_score_positive": float(scored.loc[scored["label"] == 1, "pairing_scores"].mean()),
        "mean_score_pseudo_negative": float(scored.loc[scored["label"] == 0, "pairing_scores"].mean()),
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    plot_outputs(scored, output_dir)

    print("Lightweight paper workflow completed")
    print(f"Input pairs: {dataset_path}")
    print(f"Scored pairs: {scored_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

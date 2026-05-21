from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def save_comparison_figure(baseline: dict, improved: dict, output_dir: Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams.update({"axes.spines.right": False, "axes.spines.top": False, "legend.frameon": False})

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.8))
    axes = axes.ravel()
    names = ["Original", "Improved"]

    runtimes = [baseline["runtime_sec"], improved["runtime_sec"]]
    colors = ["#8DA0CB", "#66C2A5"]
    axes[0].bar(names, runtimes, color=colors)
    axes[0].set_ylabel("Runtime (s)")
    axes[0].set_title("Speed on the same benchmark")
    axes[0].text(0.5, max(runtimes) * 1.03, f"{improved['speedup_vs_original']:.2f}x faster", ha="center", va="bottom")

    aucs = [baseline["auc_roc"], improved["auc_roc"]]
    axes[1].bar(names, aucs, color=colors)
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel("AUC-ROC")
    axes[1].set_title("Ranking performance")
    for idx, auc in enumerate(aucs):
        axes[1].text(idx, auc + 0.02, f"{auc:.3f}", ha="center")

    accs = [baseline["accuracy"], improved["accuracy"]]
    axes[2].bar(names, accs, color=colors)
    axes[2].set_ylim(0, 1)
    axes[2].set_ylabel("Accuracy")
    axes[2].set_title("Thresholded classification")
    for idx, acc in enumerate(accs):
        axes[2].text(idx, acc + 0.02, f"{acc:.3f}", ha="center")

    f1s = [baseline["f1"], improved["f1"]]
    axes[3].bar(names, f1s, color=colors)
    axes[3].set_ylim(0, 1)
    axes[3].set_ylabel("F1")
    axes[3].set_title("Balanced decision quality")
    for idx, f1 in enumerate(f1s):
        axes[3].text(idx, f1 + 0.02, f"{f1:.3f}", ha="center")

    fig.suptitle("Original vs Improved ImmunoMatch Workflow: Same Benchmark Split")
    fig.tight_layout()
    fig.savefig(output_dir / "original_vs_improved_benchmark.svg", bbox_inches="tight")
    fig.savefig(output_dir / "original_vs_improved_benchmark.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

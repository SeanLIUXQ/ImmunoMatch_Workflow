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

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    names = ["Original", "Improved"]

    runtimes = [baseline["runtime_sec"], improved["runtime_sec"]]
    colors = ["#8DA0CB", "#66C2A5"]
    axes[0].bar(names, runtimes, color=colors)
    axes[0].set_ylabel("Runtime (s)")
    axes[0].set_title("Speed")
    axes[0].text(0.5, max(runtimes) * 1.03, f"{baseline['speedup_vs_original']:.1f}x speedup", ha="center", va="bottom")

    accs = [baseline["accuracy"], improved["accuracy"]]
    axes[1].bar(names, accs, color=colors)
    axes[1].set_ylim(0, 1)
    axes[1].set_ylabel("Accuracy")
    axes[1].set_title("Accuracy")
    for idx, acc in enumerate(accs):
        axes[1].text(idx, acc + 0.02, f"{acc:.3f}", ha="center")

    fig.suptitle("Original vs Improved ImmunoMatch Workflow")
    fig.tight_layout()
    fig.savefig(output_dir / "original_vs_improved_benchmark.svg", bbox_inches="tight")
    fig.savefig(output_dir / "original_vs_improved_benchmark.png", dpi=220, bbox_inches="tight")
    plt.close(fig)

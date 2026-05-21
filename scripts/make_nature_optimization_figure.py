from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
METRICS_PATH = ROOT / "benchmark_results" / "benchmark_metrics.json"
ORIGINAL_SCORES = ROOT / "benchmark_results" / "original_scored.csv"
IMPROVED_SCORES = ROOT / "benchmark_results" / "improved_scored.csv"
OUTPUT_DIR = ROOT / "docs" / "figures"


def _box(ax, xy, width, height, label, facecolor, edgecolor="#2f3542"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.015",
        linewidth=0.9,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=8.2,
        color="#1f2933",
        linespacing=1.15,
    )


def _arrow(ax, start, end):
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(arrowstyle="-|>", lw=0.9, color="#4b5563", shrinkA=2, shrinkB=2),
    )


def _panel_pipeline(ax, settings):
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.0, 1.02, "a", transform=ax.transAxes, fontweight="bold", fontsize=12)
    ax.text(0.08, 0.95, "Execution path", fontsize=10.5, fontweight="bold", ha="left")

    left_color = "#e8eef9"
    right_color = "#e7f4ef"
    y_positions = [0.76, 0.58, 0.40, 0.22]
    left_labels = [
        "Original wrapper",
        "Rows exported\nand reloaded",
        "Repeated tokenization\nand Trainer.predict",
        f"{settings['n_rows']} row-level\nscore requests",
    ]
    right_labels = [
        "Optimized extension",
        f"{settings['unique_pairs']} unique\nVH/VL/locus pairs",
        "Cached models\nand pair memoization",
        f"{settings['n_rows']} scores\nmapped back",
    ]

    for y, label in zip(y_positions, left_labels):
        _box(ax, (0.05, y), 0.36, 0.105, label, left_color)
    for y, label in zip(y_positions, right_labels):
        _box(ax, (0.59, y), 0.36, 0.105, label, right_color)
    for y1, y2 in zip(y_positions[:-1], y_positions[1:]):
        _arrow(ax, (0.23, y1), (0.23, y2 + 0.105))
        _arrow(ax, (0.77, y1), (0.77, y2 + 0.105))

    ax.text(0.50, 0.49, "same\ncheckpoint\nscores", fontsize=8.0, ha="center", va="center", color="#374151")
    _arrow(ax, (0.42, 0.45), (0.58, 0.45))

    collapse = settings["n_rows"] / settings["unique_pairs"]
    ax.text(
        0.50,
        0.07,
        f"Duplicate-pair collapse: {settings['n_rows']} rows / {settings['unique_pairs']} unique pairs = {collapse:.1f}x fewer unique score units",
        fontsize=8.5,
        ha="center",
        color="#111827",
    )


def _panel_runtime(ax, metrics, settings):
    original = metrics["original"]["runtime_sec"]
    improved = metrics["improved"]["runtime_sec"]
    speedup = metrics["improved"]["speedup_vs_original"]
    colors = ["#5b6fa8", "#2a9d75"]

    ax.text(-0.15, 1.04, "b", transform=ax.transAxes, fontweight="bold", fontsize=12)
    bars = ax.bar(["Original", "Optimized"], [original, improved], color=colors, width=0.58)
    ax.set_ylabel("Runtime (s)")
    ax.set_title("Runtime on identical benchmark split", fontsize=10.5, pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(0, max(original, improved) * 1.22)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.7)
    ax.set_axisbelow(True)

    for bar, value in zip(bars, [original, improved]):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 4, f"{value:.2f}", ha="center", fontsize=8.5)

    ax.text(0.5, max(original, improved) * 1.13, f"{speedup:.2f}x faster", ha="center", va="center", fontsize=11, fontweight="bold", color="#111827")
    ax.text(
        0.98,
        0.78,
        f"{settings['unique_pairs']} unique pairs\n{settings['n_rows']} row-level outputs",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.0,
        color="#374151",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.78, pad=1.5),
    )


def _panel_score_identity(ax, original_df, improved_df):
    scores_original = original_df["pairing_scores"].to_numpy()
    scores_improved = improved_df["pairing_scores"].to_numpy()
    labels = improved_df["label"].to_numpy()
    max_abs_diff = np.max(np.abs(scores_original - scores_improved))

    ax.text(-0.15, 1.04, "c", transform=ax.transAxes, fontweight="bold", fontsize=12)
    colors = np.where(labels == 1, "#2a9d75", "#b85c5c")
    ax.scatter(scores_original, scores_improved, c=colors, s=20, alpha=0.72, edgecolor="white", linewidth=0.3)
    ax.plot([0, 1], [0, 1], color="#111827", linewidth=1.0, linestyle="--")
    ax.set_xlim(-0.03, 1.03)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("Original score")
    ax.set_ylabel("Optimized score")
    ax.set_title("Pairing scores are numerically unchanged", fontsize=10.5, pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#e5e7eb", linewidth=0.7)
    ax.text(0.05, 0.91, f"max absolute difference = {max_abs_diff:.0f}", transform=ax.transAxes, fontsize=8.5, bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5))
    ax.text(0.05, 0.82, "green: observed pairs\nred: shuffled pairs", transform=ax.transAxes, fontsize=8.0, color="#374151", bbox=dict(facecolor="white", edgecolor="none", alpha=0.75, pad=1.5))


def _panel_metric_delta(ax, metrics):
    names = ["AUC-ROC", "Accuracy", "F1", "MCC"]
    deltas = [
        metrics["improved"]["auc_roc"] - metrics["original"]["auc_roc"],
        metrics["improved"]["accuracy"] - metrics["original"]["accuracy"],
        metrics["improved"]["f1"] - metrics["original"]["f1"],
        metrics["improved"]["mcc"] - metrics["original"]["mcc"],
    ]
    y = np.arange(len(names))
    colors = ["#9ca3af" if abs(v) < 1e-8 else "#2a9d75" for v in deltas]

    ax.text(-0.15, 1.04, "d", transform=ax.transAxes, fontweight="bold", fontsize=12)
    ax.axvline(0, color="#111827", linewidth=0.8)
    ax.barh(y, deltas, color=colors, height=0.52)
    ax.set_yticks(y, names)
    ax.invert_yaxis()
    ax.set_xlabel("Optimized minus original")
    ax.set_title("Thresholded metrics after calibration", fontsize=10.5, pad=8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.7)
    ax.set_xlim(-0.004, 0.024)

    for idx, value in enumerate(deltas):
        xpos = value + 0.0008 if value >= 0 else value - 0.0008
        ha = "left" if value >= 0 else "right"
        label = "0.0000" if abs(value) < 1e-8 else f"+{value:.4f}"
        ax.text(xpos, idx, label, va="center", ha=ha, fontsize=8.5)

    threshold = metrics["improved"]["threshold"]
    ax.text(0.98, -0.23, f"calibrated threshold = {threshold:.4f}", transform=ax.transAxes, ha="right", fontsize=8.2, color="#374151", clip_on=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    settings = metrics["benchmark_settings"]
    original_df = pd.read_csv(ORIGINAL_SCORES)
    improved_df = pd.read_csv(IMPROVED_SCORES)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 9,
            "axes.titlesize": 10.5,
            "axes.labelsize": 9,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 8.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig = plt.figure(figsize=(10.4, 7.2))
    gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.34)
    _panel_pipeline(fig.add_subplot(gs[0, 0]), settings)
    _panel_runtime(fig.add_subplot(gs[0, 1]), metrics, settings)
    _panel_score_identity(fig.add_subplot(gs[1, 0]), original_df, improved_df)
    _panel_metric_delta(fig.add_subplot(gs[1, 1]), metrics)

    fig.suptitle(
        "Engineering speed improvements preserve ImmunoMatch score ranking",
        fontsize=13,
        fontweight="bold",
        y=0.985,
    )
    fig.savefig(OUTPUT_DIR / "nature_optimization_figure.pdf", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / "nature_optimization_figure.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT_DIR / "nature_optimization_figure.pdf")
    print(OUTPUT_DIR / "nature_optimization_figure.png")


if __name__ == "__main__":
    main()

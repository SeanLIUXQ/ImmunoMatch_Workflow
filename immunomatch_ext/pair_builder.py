from __future__ import annotations

import numpy as np
import pandas as pd


def build_lightweight_pairs(data: pd.DataFrame, n_pairs: int, seed: int = 13) -> pd.DataFrame:
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
    shuffled_vl = negatives["VL"].to_numpy().copy()
    shuffled_locus = negatives["locus"].to_numpy().copy()
    for _ in range(200):
        order = rng.permutation(len(negatives))
        if np.all(order != np.arange(len(negatives))):
            shuffled_vl = shuffled_vl[order]
            shuffled_locus = shuffled_locus[order]
            break
    else:
        order = np.roll(np.arange(len(negatives)), 1)
        shuffled_vl = shuffled_vl[order]
        shuffled_locus = shuffled_locus[order]

    negatives["VL"] = shuffled_vl
    negatives["locus"] = shuffled_locus
    negatives["pair_source"] = "shuffled_pseudo_negative"
    negatives["label"] = 0
    negatives["pair_id"] = [f"neg_{i:04d}" for i in range(len(negatives))]

    workflow = pd.concat([positives, negatives], ignore_index=True)
    workflow = workflow.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return workflow[["pair_id", "sample_name", "barcode", "VH", "VL", "locus", "pair_source", "label"]]


def build_repeated_benchmark_pairs(data: pd.DataFrame, n_pairs: int, seed: int = 13, repeats: int = 10) -> pd.DataFrame:
    base = build_lightweight_pairs(data, n_pairs=n_pairs, seed=seed)
    repeated = pd.concat([base.assign(repeat_id=i) for i in range(repeats)], ignore_index=True)
    repeated["benchmark_row_id"] = [f"row_{i:05d}" for i in range(len(repeated))]
    return repeated

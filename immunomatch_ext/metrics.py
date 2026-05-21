from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, matthews_corrcoef, precision_score, recall_score, roc_auc_score


def choose_threshold_by_accuracy(y_true, scores, grid_size: int = 400) -> tuple[float, float]:
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    if len(np.unique(scores)) == 1:
        threshold = float(scores[0])
        return threshold, float(accuracy_score(y_true, scores >= threshold))

    thresholds = np.linspace(float(scores.min()), float(scores.max()), grid_size)
    best_threshold = 0.5
    best_accuracy = -1.0
    for threshold in thresholds:
        pred = (scores >= threshold).astype(int)
        acc = accuracy_score(y_true, pred)
        if acc > best_accuracy:
            best_accuracy = acc
            best_threshold = float(threshold)
    return best_threshold, float(best_accuracy)


def summarize_scores(y_true, scores, threshold: float = 0.5) -> dict:
    y_true = np.asarray(y_true)
    scores = np.asarray(scores)
    pred = (scores >= threshold).astype(int)
    return {
        "auc_roc": float(roc_auc_score(y_true, scores)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, pred)),
        "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
        "threshold": float(threshold),
        "mean_positive_score": float(np.mean(scores[y_true == 1])) if np.any(y_true == 1) else float("nan"),
        "mean_negative_score": float(np.mean(scores[y_true == 0])) if np.any(y_true == 0) else float("nan"),
    }

# Lightweight Paper Workflow

This directory now contains a lightweight, executable reproduction of the main public ImmunoMatch workflow.

## What It Reproduces

- Uses the public GitHub example input `example_input/King_Tonsil_GC_paired.csv`.
- Treats observed single-cell heavy/light pairs as positives.
- Generates balanced pseudo-negatives by shuffling light-chain partners across observed pairs.
- Scores both observed and pseudo-negative pairs with the public kappa/lambda ImmunoMatch checkpoints.
- Computes AUC-ROC, accuracy at threshold 0.5, confusion matrix, and score summaries.
- Exports score-distribution and ROC figures as editable SVG plus PNG preview.
- Was verified on a 24-positive / 24-pseudo-negative lightweight run.

## What It Does Not Claim

- It does not retrain AntiBERTa2/ImmunoMatch from scratch.
- It does not reproduce the full original raw-data curation, donor splits, or all manuscript panels.
- The public repository contains inference and figure-analysis code, but not a full training pipeline.

## Run

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File run_lightweight_paper_workflow_windows.ps1
```

Or directly:

```powershell
.\.venv\Scripts\python.exe run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24
```

## Outputs

- `lightweight_paper_workflow/lightweight_pairs.csv`
- `lightweight_paper_workflow/lightweight_pairs_scored.csv`
- `lightweight_paper_workflow/metrics.json`
- `lightweight_paper_workflow/score_distribution.svg`
- `lightweight_paper_workflow/score_distribution.png`
- `lightweight_paper_workflow/roc_curve.svg`
- `lightweight_paper_workflow/roc_curve.png`

## Observed Lightweight Metrics

On the current workspace run, the lightweight workflow produced:

- `AUC-ROC = 0.7101`
- `accuracy@0.5 = 0.6667`
- `mean observed score = 0.7365`
- `mean pseudo-negative score = 0.4678`

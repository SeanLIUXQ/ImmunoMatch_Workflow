# Roadmap

This roadmap tracks planned improvements for the ImmunoMatch lightweight workflow reproduction.

## Completed

### Lightweight Reproduction

- Public example data workflow.
- Positive and pseudo-negative construction.
- Local kappa/lambda checkpoint inference.
- AUC-ROC, accuracy, confusion matrix, score-distribution figures.
- Bilingual GitHub README.

### Improved Engineering Layer

- Modular `immunomatch_ext/` package.
- Model cache.
- Pair-score cache.
- Duplicate-pair collapse.
- Calibrated threshold selection.
- Original vs improved benchmark.
- Benchmark comparison figure.

## Next Milestone: CLI Tooling

Implemented commands:

- `baseline`: run the original local ImmunoMatch wrapper.
- `improved`: run the improved cached scorer.
- `benchmark`: compare original and improved workflows.

Next CLI improvements:

- Add `download-models` wrapper.
- Add `build-pairs` command.
- Add `summarize-results` command.

## Future Milestone: Analysis Recipes

Potential new recipes:

- `tonsil-stage-analysis`
- `kappa-lambda-cross-test`
- `spatial-repair-comparison`
- `therapeutic-antibody-perturbation`
- `cancer-cohort-summary`

## Future Milestone: Calibration And Confidence

Potential features:

- Reliability diagrams.
- Bootstrap confidence intervals.
- Top-k candidate selection.
- Margin-based confidence scoring.
- Optional hard-negative evaluation.

## Future Milestone: Dataset Adapters

Potential adapters:

- Single-cell paired CSV adapter.
- Spatial VDJ candidate-pair adapter.
- Therapeutic antibody table adapter.
- Cancer cohort summary adapter.

# Changelog

All notable changes to this lightweight ImmunoMatch workflow are documented here.

## [0.2.0] - Improved Workflow Layer

### Added

- Added `immunomatch_ext/` as a modular extension layer that does not modify the baseline scripts.
- Added model caching through `immunomatch_ext.cache.ModelCache`.
- Added pair-score memoization and duplicate-pair collapse.
- Added `ImprovedImmunoMatchScorer` for faster local checkpoint inference.
- Added threshold calibration utilities and extended metrics.
- Added benchmark plotting utilities.
- Added `run_improved_benchmark.py` to compare original and improved workflows.
- Added benchmark outputs under `benchmark_results/`.
- Added `immunomatch_cli.py` with `baseline`, `improved`, and `benchmark` subcommands.

### Verified Benchmark

- Original runtime: `135.67 s`
- Improved runtime: `31.59 s`
- Speedup: `4.29x`
- Original accuracy: `0.6458`
- Improved accuracy: `0.6563`
- AUC-ROC unchanged: `0.6632`

### Notes

- The model weights are unchanged.
- No training is performed.
- Accuracy improvement comes from threshold calibration.
- Speed improvement comes from model caching, pair memoization, and deduplication.

## [0.1.0] - Lightweight Paper Workflow

### Added

- Added lightweight positive/pseudo-negative workflow.
- Added local checkpoint download support through `download_immunomatch_assets.py`.
- Added bilingual README files.
- Added original paper metadata in `docs/original-paper.md`.
- Added verified lightweight outputs under `lightweight_paper_workflow/`.

### Verified Lightweight Run

- Positive pairs: `24`
- Pseudo-negative pairs: `24`
- AUC-ROC: `0.7101`
- Accuracy@0.5: `0.6667`
- Mean observed score: `0.7365`
- Mean pseudo-negative score: `0.4678`

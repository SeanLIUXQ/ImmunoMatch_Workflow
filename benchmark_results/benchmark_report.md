# Original vs Improved Benchmark

## Method

- Original method: existing local ImmunoMatch wrapper with no model/pair cache and fixed threshold 0.5.
- Improved method: new `immunomatch_ext` scorer with model cache, pair-score memoization, duplicate-pair collapse, and calibrated threshold selection.
- The model weights are unchanged. No training is performed.

## Result Summary

| Metric | Original | Improved | Delta |
|---|---:|---:|---:|
| Runtime seconds | 120.620 | 29.915 | 90.705 |
| Speedup | 1.00x | 4.03x | +3.03x |
| AUC-ROC | 0.6632 | 0.6632 | 0.0000 |
| Accuracy | 0.6458 | 0.6562 | 0.0104 |
| F1 | 0.6852 | 0.6916 | 0.0064 |
| MCC | 0.3012 | 0.3210 | 0.0198 |

Improved calibrated threshold: `0.5091`

## Outputs

- `benchmark_pairs.csv`
- `original_scored.csv`
- `improved_scored.csv`
- `benchmark_metrics.json`
- `original_vs_improved_benchmark.svg`
- `original_vs_improved_benchmark.png`

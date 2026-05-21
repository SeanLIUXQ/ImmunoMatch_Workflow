# Original Paper

## Citation

Guo, D., Dunn-Walters, D.K., Fraternali, F. et al. ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains. *Nature Methods* 23, 106-117 (2026). https://doi.org/10.1038/s41592-025-02913-x

## Links

- DOI: https://doi.org/10.1038/s41592-025-02913-x
- Nature Methods article page: https://www.nature.com/articles/s41592-025-02913-x
- Official GitHub repository: https://github.com/Fraternalilab/ImmunoMatch
- Hugging Face mixed model: https://huggingface.co/fraternalilab/immunomatch
- Hugging Face kappa model: https://huggingface.co/fraternalilab/immunomatch-kappa
- Hugging Face lambda model: https://huggingface.co/fraternalilab/immunomatch-lambda

## Paper File Note

The publisher PDF is not redistributed in this repository. Please download the paper from the DOI or Nature Methods article page according to the publisher's access policy.

## How This Repository Uses The Paper

This repository implements a lightweight workflow based on the paper's public inference setup and data-construction logic:

- Observed single-cell VH/VL pairs are positives.
- Light-chain shuffling creates pseudo-negatives.
- Public ImmunoMatch checkpoints provide pairing scores.
- Lightweight metrics and figures summarize separation between observed and pseudo-negative pairs.

It does not claim to reproduce the full original training process, full raw-data curation, or all manuscript figures.

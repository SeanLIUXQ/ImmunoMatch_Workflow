# ImmunoMatch Lightweight Workflow Reproduction

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Workflow](https://img.shields.io/badge/Workflow-Lightweight%20Reproduction-green)
![Model](https://img.shields.io/badge/Model-ImmunoMatch-orange)

**A lightweight, executable reproduction workflow for ImmunoMatch inference and paper-style evaluation**

[中文](README.zh-CN.md) | [Original Paper](docs/original-paper.md) | [Quick Start](#quick-start)

</div>

---

## Overview

This repository provides a lightweight reproduction workflow for the public ImmunoMatch pipeline. It does not retrain the original model and does not attempt to rerun the full raw-data study. Instead, it makes the core paper logic executable on a local machine:

- Use observed single-cell VH/VL pairs as positives.
- Generate pseudo-negatives by shuffling light-chain partners, following the paper's core setup.
- Score VH/VL pairs with the public ImmunoMatch kappa/lambda checkpoints.
- Compute AUC-ROC, accuracy, confusion matrix, and score distributions.
- Export editable SVG figures, PNG previews, and result tables.

The workflow has been verified locally and is intended for method reproduction, teaching, and lightweight downstream extension.

## Original Paper

**Paper URL:** https://doi.org/10.1038/s41592-025-02913-x

**Citation:**

Guo, D., Dunn-Walters, D.K., Fraternali, F. et al. ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains. *Nature Methods* 23, 106-117 (2026). https://doi.org/10.1038/s41592-025-02913-x

**Original paper file note:**

- This repository does not redistribute the publisher PDF.
- Paper metadata and resource links are provided in `docs/original-paper.md`.
- Please obtain the PDF from the Nature Methods page, institutional access, or the DOI landing page.

## Relationship To The Paper

| Component | Original paper workflow | This lightweight reproduction |
|---|---|---|
| Data source | Large-scale paired single-cell BCR datasets | Public example data `King_Tonsil_GC_paired.csv` |
| Positives | VH/VL pairs observed in the same single B cell | Observed pairs from the example dataset |
| Negatives | Randomly shuffled light-chain partners | Balanced VL-shuffled pseudo-negatives |
| Model | AntiBERTa2 fine-tuned ImmunoMatch | Public kappa/lambda ImmunoMatch checkpoints |
| Training | Performed by the paper authors | Not rerun; public checkpoints are used directly |
| Inference | Pairing score for each VH/VL pair | Local checkpoint inference to produce `pairing_scores` |
| Evaluation | AUC-ROC, accuracy, confusion matrix, external validation | AUC-ROC, accuracy@0.5, confusion matrix, score distribution |
| Figures | Full manuscript figure set | Lightweight ROC and score-distribution figures |

## Verified Results

The default run uses 24 observed positives and 24 pseudo-negatives.

| Metric | Current result |
|---|---:|
| Positives | 24 |
| Pseudo-negatives | 24 |
| AUC-ROC | 0.7101 |
| Accuracy @ 0.5 | 0.6667 |
| Mean observed score | 0.7365 |
| Mean pseudo-negative score | 0.4678 |

Confusion matrix at threshold 0.5:

```text
[[12, 12],
 [ 4, 20]]
```

## Repository Layout

```text
.
├── README.md                              # Language selector
├── README.zh-CN.md                        # Chinese README
├── README.en.md                           # English README
├── docs/
│   └── original-paper.md                  # Original paper citation and resource notes
├── download_immunomatch_assets.py         # Download and cache ImmunoMatch checkpoints
├── run_immunomatch_toy.py                 # Minimal toy inference script
├── run_lightweight_paper_workflow.py      # Main lightweight paper workflow
├── run_lightweight_paper_workflow_windows.ps1
├── run_reproduction_windows.ps1
├── toy_immunomatch_input.csv
├── example_input/
│   └── King_Tonsil_GC_paired.csv          # Official small example dataset
├── lightweight_paper_workflow/            # Verified example outputs
│   ├── lightweight_pairs.csv
│   ├── lightweight_pairs_scored.csv
│   ├── metrics.json
│   ├── score_distribution.svg
│   ├── score_distribution.png
│   ├── roc_curve.svg
│   └── roc_curve.png
└── requirements_reproduced.txt
```

## Quick Start

### 1. Clone

```bash
git clone <your-repo-url>
cd ImmunoMatch_Workflow
```

### 2. Create Environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip wheel
.\.venv\Scripts\python.exe -m pip install ImmunoMatch==0.1.10 protobuf matplotlib scikit-learn
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install ImmunoMatch==0.1.10 protobuf matplotlib scikit-learn
```

### 3. Download Model Checkpoints

The default command uses a Hugging Face mirror to avoid direct-connection timeouts. The two checkpoints are about 1.6 GB in total and should not be committed to GitHub.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe download_immunomatch_assets.py --endpoint https://hf-mirror.com --model-root models --cache-dir .hf_cache
```

Linux/macOS:

```bash
python download_immunomatch_assets.py --endpoint https://hf-mirror.com --model-root models --cache-dir .hf_cache
```

If direct Hugging Face access works, use:

```bash
python download_immunomatch_assets.py --endpoint https://huggingface.co --model-root models --cache-dir .hf_cache
```

### 4. Run The Lightweight Paper Workflow

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24
```

Linux/macOS:

```bash
python run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24
```

The default input is the bundled `example_input/King_Tonsil_GC_paired.csv`. To use your own paired VH/VL CSV, pass `--input your_file.csv`.

### 5. One-Command Windows Run

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File run_lightweight_paper_workflow_windows.ps1
```

## Outputs

The workflow produces:

- `lightweight_paper_workflow/lightweight_pairs.csv`
- `lightweight_paper_workflow/lightweight_pairs_scored.csv`
- `lightweight_paper_workflow/metrics.json`
- `lightweight_paper_workflow/score_distribution.svg`
- `lightweight_paper_workflow/score_distribution.png`
- `lightweight_paper_workflow/roc_curve.svg`
- `lightweight_paper_workflow/roc_curve.png`

## FAQ

### Do I need to train the model?

No. This project uses the public pretrained ImmunoMatch checkpoints. The public repository does not include a complete training pipeline, so this project does not invent or simulate one.

### Why are `models/` not included?

The two checkpoint files are about 1.6 GB in total and are governed by the original model license. Download them with `download_immunomatch_assets.py` instead of committing them to GitHub.

### What if GitHub or Hugging Face downloads fail?

This repository supports:

- GitHub source acquisition via zip archive.
- `hf-mirror.com` endpoint.
- Resumable checkpoint downloads.

### Can I increase the sample size?

Yes. Use `--n-pairs`, for example:

```bash
python run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow_n100 --n-pairs 100
```

CPU inference will be slower. GPU acceleration is handled automatically by PyTorch/Transformers when available.

## License And Acknowledgements

This repository is intended for method reproduction and teaching. ImmunoMatch models, paper, name, and related resources belong to the original authors. Please follow the license terms of the original model pages and paper. The official ImmunoMatch README states that the models are provided under CC-BY-NC-4.0.

If you use this repository or the ImmunoMatch models, please cite the original paper:

```bibtex
@article{guo2026immunomatch,
  title = {ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains},
  author = {Guo, D. and Dunn-Walters, D. K. and Fraternali, F. and others},
  journal = {Nature Methods},
  volume = {23},
  pages = {106--117},
  year = {2026},
  doi = {10.1038/s41592-025-02913-x}
}
```

# ImmunoMatch Reproduction Report

## Scope

This reproduction used the official public materials specified by the task, with priority order GitHub repository, Colab, PyPI package, Hugging Face checkpoints, and Nature Methods paper. Full raw reference databases were not downloaded.

## Environment

Workspace: `D:\ImmunoMatch_Workflow`

Python detected: `Python 3.13.9`

Virtual environment: `.venv`

Installed official package: `ImmunoMatch==0.1.10`

Environment lockfile: `requirements_reproduced.txt`

GPU fallback: the official code uses `torch.cuda.is_available()` and therefore falls back to CPU if CUDA is unavailable. The package then performs prediction through Hugging Face `Trainer`.

## Exact Commands Run

Repository clone attempts:

```bash
git clone https://github.com/Fraternalilab/ImmunoMatch.git
git clone --depth 1 https://github.com/Fraternalilab/ImmunoMatch.git
```

Both clone attempts failed from this environment due to GitHub connectivity errors:

```text
Recv failure: Connection was reset
Failed to connect to github.com port 443
```

Environment setup:

```bash
python --version
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python -m pip install ImmunoMatch==0.1.10
.\.venv\Scripts\python -m pip install protobuf
.\.venv\Scripts\python -m pip freeze
```

Package inspection:

```bash
.\.venv\Scripts\python -c "import ImmunoMatch,inspect,os; print(ImmunoMatch.__file__); print(dir(ImmunoMatch))"
.\.venv\Scripts\python -m pip show -f ImmunoMatch
```

Checkpoint load test:

```bash
.\.venv\Scripts\python -c "from transformers import RoFormerTokenizer, RoFormerForSequenceClassification; m='fraternalilab/immunomatch-kappa'; tok=RoFormerTokenizer.from_pretrained(m); mod=RoFormerForSequenceClassification.from_pretrained(m); print(type(tok).__name__, type(mod).__name__); print(mod.config.id2label)"
```

HF API probes:

```bash
Invoke-WebRequest -UseBasicParsing https://huggingface.co/api/models/fraternalilab/immunomatch-kappa
Invoke-WebRequest -UseBasicParsing https://huggingface.co/api/models/fraternalilab/immunomatch
Invoke-WebRequest -UseBasicParsing https://huggingface.co/api/models/fraternalilab/immunomatch-lambda
```

Reproduction script to run after network access to Hugging Face is available:

```bash
bash run_reproduction.sh
```

Windows one-click launcher:

```powershell
run_reproduction_windows.cmd
```

## Official Package Code Paths Identified

Installed package location:

```text
.venv/Lib/site-packages/ImmunoMatch/run_immunomatch.py
```

Important functions:

- `preprocess_seq(example, hseqcol="input_Hseq", lseqcol="input_Lseq")`: inserts spaces between amino-acid characters for RoFormer tokenization.
- `tokenize_function(...)`: tokenizes paired H/L sequences with padding and truncation to `max_length=256`.
- `tokenize_the_datasets(df_dir, hseq_col, lseq_col, tokenizer)`: reads a CSV and maps preprocessing/tokenization through Hugging Face `datasets`.
- `pairing_scores_batches(df_dir, hseq_col, lseq_col, model_checkpoint)`: loads tokenizer/model from a Hugging Face checkpoint, predicts logits with `Trainer.predict`, and returns `softmax(logits)[:, 1]` as `pairing_scores`.
- `run_immunomatch_batches(data, hseq_col, lseq_col, ltype_col)`: splits a DataFrame by `IGK` and `IGL`, runs `fraternalilab/immunomatch-kappa` and `fraternalilab/immunomatch-lambda`, concatenates results, and restores original order.

No console entry point was found. The public interface is Python API usage:

```python
from ImmunoMatch import run_immunomatch_batches
result = run_immunomatch_batches(data, "VH", "VL", "light_chain_type")
```

## Inference Reproduction

Created toy input:

```text
toy_immunomatch_input.csv
```

Created runner:

```text
run_immunomatch_toy.py
```

The runner uses the official API and writes:

```text
toy_immunomatch_output.csv
```

Inference could not complete in this environment because all attempts to reach Hugging Face timed out. The local missing dependency `protobuf` was fixed, after which the remaining error was repeated timeout resolving files such as:

```text
https://huggingface.co/fraternalilab/immunomatch-kappa/resolve/main/tokenizer_config.json
https://huggingface.co/fraternalilab/immunomatch-kappa/resolve/main/vocab.txt
https://huggingface.co/fraternalilab/immunomatch-kappa/resolve/main/config.json
```

The final observed exception was caused by unavailable tokenizer files after the failed downloads:

```text
TypeError: _path_isfile: path should be string, bytes, os.PathLike or integer, not NoneType
```

The script should run without code changes in an environment that can access the Hugging Face model repositories.

## Training and Evaluation Reproduction

The public PyPI package does not expose a training script or training function. It imports `Trainer` and `TrainingArguments`, but only uses them for prediction. No minimal training pass was run because doing so would require inventing unsupported training behavior. The paper describes training conceptually as fine-tuning an antibody-specific transformer on balanced positive and shuffled pseudo-negative pairs, but the exact training pipeline was not present in the installed package.

## Paper-Derived ML Summary

The Nature Methods paper frames ImmunoMatch as binary classification of cognate versus pseudo-negative H-L chain pairs. Positive examples are single-cell observed pairs. Pseudo-negatives are generated by shuffling light-chain partners. The final model is based on AntiBERTa2 and outperforms V/J-gene-only and CDR3-only baselines. The paper reports AUC-ROC about 0.75 for the final mixed model on a withheld set and about 0.66 on an external unseen-donor set. Specialized kappa/lambda models improve reported accuracy for their matching light-chain types.

## Files Touched

- `requirements_reproduced.txt`: exact installed package versions.
- `toy_immunomatch_input.csv`: tiny synthetic VH/VL input table matching the package schema.
- `run_immunomatch_toy.py`: official-API runner for toy inference.
- `run_reproduction.sh`: end-to-end setup and inference script.
- `run_reproduction_windows.ps1`: Windows PowerShell one-click reproduction script.
- `run_reproduction_windows.cmd`: double-click Windows launcher for the PowerShell script.
- `workflow_summary.md`: plain-English ML workflow summary.
- `reproduction_report.md`: this report.

## Blockers

- GitHub repository clone failed from this environment due to connection reset/timeout.
- Colab and Hugging Face HTML pages were inaccessible through the available fetch tools.
- Hugging Face checkpoint files could not be downloaded through `transformers` or PowerShell due to network timeouts.
- PyPI was accessible, so the official installable package was used to inspect code paths and build the reproduction harness.

## Next Steps

1. Run `bash run_reproduction.sh` on a machine with direct access to `huggingface.co`.
2. If the GitHub repository becomes accessible, compare the PyPI package against `README.md`, `Run_ImmunoMatch.ipynb`, and any training scripts in the repository.
3. If training scripts exist in the repository, run a true 2-epoch toy fine-tuning pass using official code only.
4. For larger inference jobs, add a non-invasive cache of repeated `(VH, VL, light_chain_type)` pairs before calling the official scorer to avoid duplicate transformer inference.

## Lightweight Paper Workflow Added Later

The workspace now also contains a lightweight end-to-end paper-style workflow:

- `run_lightweight_paper_workflow.py`
- `run_lightweight_paper_workflow_windows.ps1`
- `lightweight_workflow_README.md`

This workflow uses the public example tonsil paired dataset, constructs balanced pseudo-negatives by shuffling light-chain partners, scores them with the locally cached ImmunoMatch checkpoints, and exports metrics plus SVG/PNG plots.

Verified run outputs:

- `lightweight_paper_workflow/lightweight_pairs.csv`
- `lightweight_paper_workflow/lightweight_pairs_scored.csv`
- `lightweight_paper_workflow/metrics.json`
- `lightweight_paper_workflow/score_distribution.svg`
- `lightweight_paper_workflow/roc_curve.svg`

Observed metrics from the verified run:

- AUC-ROC: 0.7101
- accuracy at 0.5: 0.6667
- mean observed score: 0.7365
- mean pseudo-negative score: 0.4678

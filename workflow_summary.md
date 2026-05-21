# ImmunoMatch Workflow Summary

## Plain-English Model Summary

ImmunoMatch predicts whether an antibody heavy-chain variable domain and light-chain variable domain form a cognate, biologically compatible pair. The user supplies full-length VH and VL amino-acid sequences plus the light-chain type, and the package returns a pairing score interpreted as the probability-like score for a cognate pair.

## Inputs and Outputs

Input rows contain at least three fields:

- Heavy-chain variable-region amino-acid sequence, such as `VH`.
- Light-chain variable-region amino-acid sequence, such as `VL`.
- Light-chain type, where the official batch wrapper dispatches rows containing `IGK` to the kappa-specific model and rows containing `IGL` to the lambda-specific model.

The output is the original table with a `pairing_scores` column. In the official package, this score is computed as `softmax(logits)[:, 1]` from a two-class RoFormer sequence-classification model.

## Positive Examples

The paper defines positive examples as paired heavy and light chains observed in the same single B cell. The core assumption is that single-cell barcode co-occurrence of one H chain and one L chain identifies a real cognate antibody pair.

## Pseudo-Negative Examples

True nonviable negative H-L pairs cannot be directly observed because natural selection removes many unstable or autoreactive B cells. The paper therefore constructs pseudo-negatives by random shuffling: light-chain partners are exchanged across observed positive pairs. This creates balanced binary-classification data with matched counts of positive and pseudo-negative rows.

## Architecture

The model family is a transformer-based antibody language-model classifier. The paper reports that ImmunoMatch is based on AntiBERTa2, an antibody-specific language model, fine-tuned for binary H-L pairing classification. The PyPI package loads Hugging Face checkpoints with `transformers.RoFormerTokenizer` and `transformers.RoFormerForSequenceClassification`, tokenizes VH and VL as paired sequences, and predicts batched scores through a Hugging Face `Trainer`.

The public checkpoints described by the official package are:

- `fraternalilab/immunomatch`: trained on mixed kappa and lambda light chains.
- `fraternalilab/immunomatch-kappa`: trained on H-kappa pairs.
- `fraternalilab/immunomatch-lambda`: trained on H-lambda pairs.

The public batch API uses the kappa and lambda specialized checkpoints, not the mixed checkpoint.

## Reported Metrics

From the Nature Methods paper text available during this reproduction:

- Final mixed ImmunoMatch model: test AUC-ROC about 0.75 on the withheld test set.
- External unseen-donor evaluation: AUC-ROC about 0.66.
- Kappa-specific model: reported accuracy about 0.817 on kappa data.
- Lambda-specific model: reported accuracy about 0.764 on lambda data.

The paper also discusses accuracy, ROC curves, AUC-ROC, and confusion matrices for model variants.

## Likely Bottlenecks

The main bottlenecks are model download, transformer inference cost, and all-by-all candidate scoring when reconstructing pairs from unpaired repertoires or spatial VDJ data. For small CSV inputs the package is straightforward. For large candidate-pair matrices, score computation scales with the number of tested H-L combinations, so batching, GPU availability, and avoiding duplicate sequence-pair scoring become important.

## Training Support in Public Package

The PyPI package imports `Trainer` and `TrainingArguments`, but it does not expose a training or fine-tuning function. The distributed code exposes inference/tokenization utilities only. Minimal training was therefore not reproduced without inventing unsupported functionality.

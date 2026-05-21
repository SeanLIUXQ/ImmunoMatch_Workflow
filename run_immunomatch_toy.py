import argparse
from pathlib import Path

import pandas as pd
import torch
from ImmunoMatch import pairing_scores_batches, run_immunomatch_batches


def run_immunomatch_batches_local(data, hseq_col, lseq_col, ltype_col, model_root: Path):
    kappa_data = data.loc[data[ltype_col].apply(lambda x: "IGK" in x)]
    lambda_data = data.loc[data[ltype_col].apply(lambda x: "IGL" in x)]

    k_data_dir = "kappa_data.csv"
    l_data_dir = "lambda_data.csv"
    kappa_data.to_csv(k_data_dir)
    lambda_data.to_csv(l_data_dir)

    kappa_model = model_root / "immunomatch-kappa"
    lambda_model = model_root / "immunomatch-lambda"
    k_result = pairing_scores_batches(k_data_dir, hseq_col, lseq_col, str(kappa_model))
    l_result = pairing_scores_batches(l_data_dir, hseq_col, lseq_col, str(lambda_model))
    return pd.concat([k_result, l_result]).sort_values(by=["Unnamed: 0"]).drop(columns=["Unnamed: 0"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run official ImmunoMatch batch inference on a toy CSV.")
    parser.add_argument("--input", default="toy_immunomatch_input.csv")
    parser.add_argument("--output", default="toy_immunomatch_output.csv")
    parser.add_argument("--model-root", default=None, help="Optional local directory containing immunomatch-kappa and immunomatch-lambda.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = pd.read_csv(input_path)
    print(f"Loaded {len(data)} toy pairs from {input_path}")
    print(f"torch.cuda.is_available()={torch.cuda.is_available()}")

    if args.model_root:
        result = run_immunomatch_batches_local(
            data,
            hseq_col="VH",
            lseq_col="VL",
            ltype_col="light_chain_type",
            model_root=Path(args.model_root),
        )
    else:
        result = run_immunomatch_batches(
            data,
            hseq_col="VH",
            lseq_col="VL",
            ltype_col="light_chain_type",
        )
    result.to_csv(output_path, index=False)
    print(f"Wrote ImmunoMatch scores to {output_path}")
    print(result[["pair_id", "light_chain_type", "pairing_scores"]].to_string(index=False))


if __name__ == "__main__":
    main()

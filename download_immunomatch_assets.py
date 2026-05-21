import argparse
import shutil
import time
from pathlib import Path

import requests
from huggingface_hub import HfApi, hf_hub_download


DEFAULT_ENDPOINT = "https://hf-mirror.com"
REPOS = {
    "kappa": "fraternalilab/immunomatch-kappa",
    "lambda": "fraternalilab/immunomatch-lambda",
}
SMALL_FILES = [
    "config.json",
    "special_tokens_map.json",
    "tokenizer_config.json",
    "vocab.txt",
]
WEIGHT_FILE = "pytorch_model.bin"


def download_stream(url: str, target: Path, chunk_size: int = 8 * 1024 * 1024, retries: int = 12) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    for attempt in range(1, retries + 1):
        resume_from = tmp.stat().st_size if tmp.exists() else 0
        headers = {"User-Agent": "ImmunoMatch-reproduction/1.0"}
        if resume_from:
            headers["Range"] = f"bytes={resume_from}-"

        try:
            with requests.get(url, headers=headers, stream=True, timeout=(20, 300)) as response:
                if response.status_code == 416:
                    tmp.replace(target)
                    return
                response.raise_for_status()
                mode = "ab" if resume_from and response.status_code == 206 else "wb"
                if mode == "wb":
                    resume_from = 0
                total = response.headers.get("Content-Length")
                total_text = f"/{int(total) + resume_from:,}" if total and total.isdigit() else ""
                written = resume_from
                with tmp.open(mode) as handle:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        written += len(chunk)
                        print(f"  {target.name}: {written:,}{total_text} bytes", end="\r", flush=True)
            print()
            tmp.replace(target)
            return
        except requests.RequestException as exc:
            if attempt == retries:
                raise
            print(f"\n  retrying {target.name} after download error ({attempt}/{retries}): {exc}")
            time.sleep(min(30, 2 * attempt))


def prepare_model(repo_id: str, model_dir: Path, endpoint: str, cache_dir: Path) -> None:
    print(f"Preparing {repo_id} -> {model_dir}")
    model_dir.mkdir(parents=True, exist_ok=True)

    api = HfApi(endpoint=endpoint)
    api.model_info(repo_id)

    for filename in SMALL_FILES:
        cached = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            endpoint=endpoint,
            cache_dir=str(cache_dir),
            force_download=False,
        )
        shutil.copy2(cached, model_dir / filename)
        print(f"  copied {filename}")

    weight_target = model_dir / WEIGHT_FILE
    if weight_target.exists() and weight_target.stat().st_size > 0:
        print(f"  existing {WEIGHT_FILE}: {weight_target.stat().st_size:,} bytes")
        return

    direct_url = f"{endpoint.rstrip('/')}/{repo_id}/resolve/main/{WEIGHT_FILE}"
    download_stream(direct_url, weight_target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download ImmunoMatch checkpoints through a mirror into local model directories.")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model-root", default="models")
    parser.add_argument("--cache-dir", default=".hf_cache")
    parser.add_argument("--only", choices=["kappa", "lambda", "all"], default="all")
    args = parser.parse_args()

    model_root = Path(args.model_root)
    cache_dir = Path(args.cache_dir)
    keys = REPOS.keys() if args.only == "all" else [args.only]
    for key in keys:
        prepare_model(REPOS[key], model_root / f"immunomatch-{key}", args.endpoint, cache_dir)


if __name__ == "__main__":
    main()

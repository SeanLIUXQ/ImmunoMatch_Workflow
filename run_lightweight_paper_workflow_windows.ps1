$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$env:HF_ENDPOINT = if ($env:HF_ENDPOINT) { $env:HF_ENDPOINT } else { "https://hf-mirror.com" }
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"

if (-not (Test-Path -LiteralPath $VenvPython)) {
    python -m venv .venv
}

& $VenvPython -m pip install --upgrade pip wheel
& $VenvPython -m pip install ImmunoMatch==0.1.10 protobuf matplotlib scikit-learn
& $VenvPython download_immunomatch_assets.py --endpoint $env:HF_ENDPOINT --model-root models --cache-dir .hf_cache
& $VenvPython run_lightweight_paper_workflow.py --model-root models --output-dir lightweight_paper_workflow --n-pairs 24

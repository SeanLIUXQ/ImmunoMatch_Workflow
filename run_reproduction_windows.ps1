$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $Root

$LogPath = Join-Path $Root "windows_reproduction_log.txt"
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$InputCsv = Join-Path $Root "toy_immunomatch_input.csv"
$OutputCsv = Join-Path $Root "toy_immunomatch_output.csv"
$ModelRoot = Join-Path $Root "models"
$env:HF_ENDPOINT = if ($env:HF_ENDPOINT) { $env:HF_ENDPOINT } else { "https://hf-mirror.com" }
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = "1"

function Write-Step {
    param([string]$Message)
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $Message"
    $line | Tee-Object -FilePath $LogPath -Append
}

if (Test-Path -LiteralPath $LogPath) {
    Remove-Item -LiteralPath $LogPath -Force
}

Write-Step "Starting ImmunoMatch Windows reproduction run."
Write-Step "Workspace: $Root"

if (-not (Test-Path -LiteralPath $InputCsv)) {
    throw "Missing input file: $InputCsv"
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Step "Creating virtual environment at .venv"
    python -m venv .venv 2>&1 | Tee-Object -FilePath $LogPath -Append
} else {
    Write-Step "Using existing virtual environment at .venv"
}

Write-Step "Upgrading packaging tools."
& $VenvPython -m pip install --upgrade pip wheel 2>&1 | Tee-Object -FilePath $LogPath -Append

Write-Step "Installing official ImmunoMatch package and protobuf."
& $VenvPython -m pip install ImmunoMatch==0.1.10 protobuf 2>&1 | Tee-Object -FilePath $LogPath -Append

Write-Step "Saving reproduced environment to requirements_reproduced.txt."
& $VenvPython -m pip freeze | Out-File -FilePath (Join-Path $Root "requirements_reproduced.txt") -Encoding ascii

Write-Step "Downloading ImmunoMatch model assets from $env:HF_ENDPOINT."
& $VenvPython download_immunomatch_assets.py --endpoint $env:HF_ENDPOINT --model-root $ModelRoot --cache-dir (Join-Path $Root ".hf_cache") 2>&1 | Tee-Object -FilePath $LogPath -Append
if ($LASTEXITCODE -ne 0) {
    throw "Model asset download exited with code $LASTEXITCODE"
}

Write-Step "Running official ImmunoMatch toy inference."
try {
    $PreviousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $VenvPython run_immunomatch_toy.py --input $InputCsv --output $OutputCsv --model-root $ModelRoot 2>&1 | Tee-Object -FilePath $LogPath -Append
    $ErrorActionPreference = $PreviousErrorActionPreference
    if ($LASTEXITCODE -ne 0) {
        throw "Inference command exited with code $LASTEXITCODE"
    }
    Write-Step "Inference finished. Output: $OutputCsv"
} catch {
    $ErrorActionPreference = "Stop"
    Write-Step "Inference did not complete. Most likely blocker: this machine cannot download Hugging Face checkpoints fraternalilab/immunomatch-kappa and fraternalilab/immunomatch-lambda."
    Write-Step "Original error: $($_.Exception.Message)"
    Write-Step "If Hugging Face access is restored, rerun run_reproduction_windows.cmd."
    exit 1
}

Write-Step "Done."

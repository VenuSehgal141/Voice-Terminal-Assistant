# PowerShell installer wrapper for Windows
# Usage: .\install.ps1 [-Backend <google|sphinx|none>]

param(
    [string]$Backend = ""
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if (-not (Test-Path venv)) {
    Write-Output "Creating virtual environment..."
    python -m venv venv
} else {
    Write-Output "venv already present"
}

# Use venv python directly to avoid requiring activation in this script
$venvPython = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Output "Warning: venv python not found, falling back to system python"
    $venvPython = "python"
}

Write-Output "Upgrading pip, setuptools, wheel..."
& $venvPython -m pip install --upgrade pip setuptools wheel

Write-Output "Installing core packages..."
& $venvPython -m pip install SpeechRecognition pyaudio pydub python-dotenv

Write-Output "Note: pocketsphinx is optional on Windows and often requires build tools."
Write-Output "If you need offline recognition, install a matching pocketsphinx wheel or follow README instructions."

if ($Backend -ne "") {
    Write-Output "Persisting VOICE_BACKEND=$Backend to .env"
    $envPath = Join-Path $root ".env"
    if (Test-Path $envPath) {
        (Get-Content $envPath) | ForEach-Object {
            if ($_ -match '^VOICE_BACKEND=') {
                "VOICE_BACKEND=$Backend"
            } else {
                $_
            }
        } | Set-Content $envPath

        if (-not (Select-String -Path $envPath -Pattern '^VOICE_BACKEND=' -Quiet)) {
            Add-Content $envPath "VOICE_BACKEND=$Backend"
        }
    } else {
        Set-Content $envPath "VOICE_BACKEND=$Backend"
    }
}

Write-Output "\nDone. Quick start:"
Write-Output "  - Run with venv Python without activating: .\venv\Scripts\python.exe main.py"
Write-Output "  - Or activate and run: .\venv\Scripts\Activate.ps1; python main.py"
Write-Output "  - Or use bootstrap helper: python bootstrap.py run --use-venv"

Write-Output "If you set a backend (e.g. -Backend sphinx), the choice was written to .env"
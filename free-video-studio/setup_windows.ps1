<#
  Free Video Studio - Windows setup
  Installs the free tools for making 2.5D cartoon shorts.

  Usage (PowerShell, inside the free-video-studio folder):
    Set-ExecutionPolicy -Scope Process Bypass
    .\setup_windows.ps1                 # core: Git, Python, FFmpeg, captions (faster-whisper), fonts
    .\setup_windows.ps1 -WithImages     # + ComfyUI + SD 1.5 cartoon-capable model (~2 GB) for still images
    .\setup_windows.ps1 -WithBlender    # + Blender (optional 3D)

  Safe to run again: it skips anything already installed.
#>
param(
    [switch]$WithImages,
    [switch]$WithBlender
)

$ErrorActionPreference = "Stop"
$Root  = $PSScriptRoot
$Tools = Join-Path $Root "tools"
New-Item -ItemType Directory -Force -Path $Tools, "$Root\assets\fonts", "$Root\assets\sfx", "$Root\assets\music", "$Root\projects" | Out-Null

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
}
function Winget-Install($id, $name) {
    Write-Host "Installing $name ..."
    winget install --id $id -e --accept-source-agreements --accept-package-agreements --silent
    Refresh-Path
}
function Download($url, $dest) {
    if ((Test-Path $dest) -and ((Get-Item $dest).Length -gt 10000)) { Write-Host "  have $(Split-Path $dest -Leaf)"; return }
    Write-Host "  downloading $(Split-Path $dest -Leaf) ..."
    curl.exe -L --fail --retry 3 -o $dest $url
}

if (-not (Have "winget")) {
    throw "winget not found. Install 'App Installer' from the Microsoft Store, then run this again."
}

# ---------------------------------------------------------------- core tools
Step "Core tools: Git, Python 3.11, FFmpeg"
if (-not (Have "git"))    { Winget-Install "Git.Git" "Git" }
if (-not (Have "ffmpeg")) { Winget-Install "Gyan.FFmpeg" "FFmpeg" }
$py311 = $false
try { & py -3.11 --version | Out-Null; $py311 = $true } catch {}
if (-not $py311) { Winget-Install "Python.Python.3.11" "Python 3.11" }

# ---------------------------------------------------------------- captions
Step "Caption tools (faster-whisper, runs on CPU)"
$Venv = Join-Path $Root ".venv"
if (-not (Test-Path "$Venv\Scripts\python.exe")) { & py -3.11 -m venv $Venv }
$Py = "$Venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip --quiet
& $Py -m pip install --quiet faster-whisper pillow numpy
Write-Host "  pre-downloading Whisper 'small' model (~500 MB) ..."
& $Py -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='int8'); print('  whisper ready')"

# ---------------------------------------------------------------- fonts
Step "Caption fonts (Google Fonts, free)"
$F = "$Root\assets\fonts"
Download "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-ExtraBold.ttf" "$F\Poppins-ExtraBold.ttf"
Download "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Black.ttf"     "$F\Poppins-Black.ttf"
Download "https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf" "$F\LuckiestGuy-Regular.ttf"

# ---------------------------------------------------------------- images (optional)
if ($WithImages) {
    Step "ComfyUI for still images (Quadro P1000 / Pascal compatible)"
    $Comfy = Join-Path $Tools "ComfyUI"
    if (-not (Test-Path $Comfy)) { git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git $Comfy }
    $CN = "$Comfy\custom_nodes"
    if (-not (Test-Path "$CN\ComfyUI-Manager")) { git clone --depth 1 https://github.com/Comfy-Org/ComfyUI-Manager.git "$CN\ComfyUI-Manager" }
    if (-not (Test-Path "$CN\ComfyUI-GGUF"))    { git clone --depth 1 https://github.com/city96/ComfyUI-GGUF.git "$CN\ComfyUI-GGUF" }

    $CVenv = "$Comfy\.venv"
    if (-not (Test-Path "$CVenv\Scripts\python.exe")) { & py -3.11 -m venv $CVenv }
    $CPy = "$CVenv\Scripts\python.exe"
    & $CPy -m pip install --upgrade pip --quiet
    # Pascal (P1000) is not supported by CUDA 12.8+ PyTorch builds -> use CUDA 12.6
    & $CPy -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
    & $CPy -m pip install -r "$Comfy\requirements.txt" --quiet
    & $CPy -m pip install -r "$CN\ComfyUI-GGUF\requirements.txt" --quiet
    & $CPy -c "import torch; print('  GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT DETECTED - check NVIDIA driver')"

    Step "SD 1.5 model (~2 GB)"
    Download "https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive/resolve/main/v1-5-pruned-emaonly-fp16.safetensors" `
             "$Comfy\models\checkpoints\v1-5-pruned-emaonly-fp16.safetensors"
    Write-Host "  Tip: add a cartoon-style SD 1.5 model from civitai.com into $Comfy\models\checkpoints"

    # Launcher: --lowvram keeps memory use inside 4 GB
    "@echo off`r`ncd /d `"%~dp0tools\ComfyUI`"`r`n.venv\Scripts\python.exe main.py --lowvram --preview-method auto`r`npause" |
        Set-Content -Encoding ASCII "$Root\start_comfyui.bat"
    Write-Host "  Start it with start_comfyui.bat, then open http://127.0.0.1:8188"
}

# ---------------------------------------------------------------- Blender (optional)
if ($WithBlender) {
    Step "Blender"
    if (-not (Test-Path "$env:ProgramFiles\Blender Foundation")) { Winget-Install "BlenderFoundation.Blender" "Blender" }
    Write-Host "  Free extras: Mixamo (character animations), Kenney.nl (CC0 3D assets), Poly Haven (HDRIs/textures)"
}

# ---------------------------------------------------------------- check
Step "Check"
Refresh-Path
foreach ($c in "git", "ffmpeg") { Write-Host ("  {0,-8} {1}" -f $c, $(if (Have $c) { "OK" } else { "MISSING - reopen PowerShell and run again" })) }
Write-Host "  python   $(& $Py --version)"
Write-Host "`nDone. Next: download free sound effects and music with assets\DOWNLOAD_LIST.md" -ForegroundColor Green
Write-Host "AI video (image -> clip) runs on Kaggle: ..\kaggle\wan22_image_to_video.ipynb" -ForegroundColor Green

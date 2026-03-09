param(
    [switch]$SkipBridgeRun
)

$ErrorActionPreference = "Stop"

function Assert-Command {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        throw "Missing required path: $Path"
    }
}

Write-Host "Voice smoke test: Silero primary"

Assert-Command ".\.venv\Scripts\python.exe"
Assert-Command ".\.env"

$requiredVars = @(
    "OPENCLAW_GATEWAY_TOKEN",
    "TTS_PROVIDER",
    "SILERO_MODEL_SOURCE",
    "SILERO_LANGUAGE",
    "SILERO_MODEL_ID",
    "SILERO_SPEAKER"
)

$envLines = Get-Content .\.env
$envMap = @{}
foreach ($line in $envLines) {
    if ($line -match '^\s*#' -or $line -notmatch '=') {
        continue
    }
    $parts = $line.Split('=', 2)
    $envMap[$parts[0].Trim()] = $parts[1].Trim()
}

foreach ($name in $requiredVars) {
    if (-not $envMap.ContainsKey($name) -or [string]::IsNullOrWhiteSpace($envMap[$name])) {
        throw "Missing required .env value: $name"
    }
}

if ($envMap["TTS_PROVIDER"] -ne "silero") {
    throw "Expected TTS_PROVIDER=silero in .env"
}

if ($envMap.ContainsKey("TTS_FALLBACK_PROVIDER") -and $envMap["TTS_FALLBACK_PROVIDER"] -ne "") {
    throw "Expected TTS_FALLBACK_PROVIDER to be empty for the out-of-box Silero setup"
}

Write-Host "1. Config looks valid"

Write-Host "2. Verifying Python runtime imports"
.\.venv\Scripts\python.exe -c "import pygame, requests, soundfile, torch; print('runtime imports ok')"

Write-Host "3. Verifying config bootstrap"
.\.venv\Scripts\python.exe -c "from openclaw_voice.config import VoiceConfig; cfg = VoiceConfig.from_env(); print(cfg.tts_provider, cfg.tts_fallback_provider)"

Write-Host "4. Verifying Silero model bootstrap"
.\.venv\Scripts\python.exe -c "from openclaw_voice.config import VoiceConfig; from openclaw_voice.services.tts_service import build_tts_service; cfg = VoiceConfig.from_env(); service = build_tts_service(cfg); provider = service.primary_provider; print(provider.name)"

if ($SkipBridgeRun) {
    Write-Host "5. Bridge run skipped by flag"
    exit 0
}

Write-Host "5. Manual bridge smoke run"
Write-Host "   - Run .\run.bat"
Write-Host "   - Say the wake word"
Write-Host "   - Ask one short Russian question"
Write-Host "   - Confirm logs show speech recognition, OpenClaw request, and TTS playback"
Write-Host "   - Confirm reply returns through Silero"

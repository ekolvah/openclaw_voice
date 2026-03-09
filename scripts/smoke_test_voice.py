from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

REQUIRED_ENV_VARS = (
    "OPENCLAW_GATEWAY_TOKEN",
    "TTS_PROVIDER",
    "SILERO_MODEL_SOURCE",
    "SILERO_LANGUAGE",
    "SILERO_MODEL_ID",
    "SILERO_SPEAKER",
)


def _parse_env_file(path: Path) -> dict[str, str]:
    env_map: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_map[key.strip()] = value.strip()
    return env_map


def _require_path(path: Path) -> None:
    if not path.exists():
        raise RuntimeError(f"Missing required path: {path}")


def _assert_config(env_map: dict[str, str]) -> None:
    missing = [
        name
        for name in REQUIRED_ENV_VARS
        if name not in env_map or not env_map[name].strip()
    ]
    if missing:
        raise RuntimeError(f"Missing required .env values: {', '.join(missing)}")

    if env_map["TTS_PROVIDER"] != "silero":
        raise RuntimeError("Expected TTS_PROVIDER=silero in .env")

    if env_map.get("TTS_FALLBACK_PROVIDER", ""):
        raise RuntimeError(
            "Expected TTS_FALLBACK_PROVIDER to be empty for the out-of-box Silero setup"
        )


def _check_imports() -> None:
    for module_name in ("pygame", "requests", "soundfile", "torch"):
        importlib.import_module(module_name)


def _check_runtime_bootstrap() -> None:
    from openclaw_voice.config import VoiceConfig
    from openclaw_voice.services.tts_service import build_tts_service

    config = VoiceConfig.from_env()
    service = build_tts_service(config)
    print(f"tts_provider={config.tts_provider} fallback={config.tts_fallback_provider}")
    print(f"primary_provider={service.primary_provider.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for the Silero voice runtime.")
    parser.add_argument(
        "--skip-bridge-run",
        action="store_true",
        help="Validate config and runtime only, without the manual bridge checklist.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    python_path = repo_root / ".venv" / "Scripts" / "python.exe"
    env_path = repo_root / ".env"

    print("Voice smoke test: Silero primary")
    _require_path(python_path)
    _require_path(env_path)

    env_map = _parse_env_file(env_path)
    _assert_config(env_map)
    print("1. Config looks valid")

    _check_imports()
    print("2. Runtime imports ok")

    _check_runtime_bootstrap()
    print("3. Config bootstrap ok")
    print("4. Silero provider bootstrap ok")

    if args.skip_bridge_run:
        print("5. Bridge run skipped by flag")
        return 0

    print("5. Manual bridge smoke run")
    print("   - Run .\\run.bat")
    print("   - Say the wake word")
    print("   - Ask one short Russian question")
    print("   - Confirm logs show speech recognition, OpenClaw request, and TTS playback")
    print("   - Confirm reply returns through Silero")
    return 0


if __name__ == "__main__":
    sys.exit(main())

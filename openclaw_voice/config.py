"""Configuration loading for OpenClaw voice bridge.

Environment variables:
- OPENCLAW_GATEWAY_URL
- OPENCLAW_GATEWAY_TOKEN
- OPENCLAW_AGENT_ID
- EDGE_TTS_VOICE
- WAKE_WORD
- WAKE_SENSITIVITY
- SILENCE_SECONDS
- HISTORY_LIMIT
- VOICE_LOCK_FILE
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, str(default)).strip()
    try:
        return float(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid float for {name}: {raw}") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid int for {name}: {raw}") from exc


@dataclass(frozen=True)
class VoiceConfig:
    """Static runtime configuration loaded from .env."""

    openclaw_gateway_url: str
    openclaw_gateway_token: str
    openclaw_agent_id: str
    tts_voice: str
    wake_word: str
    wake_sensitivity: float
    silence_seconds: float
    history_limit: int
    log_file: str = "voice_bridge.log"
    lock_file: str = "voice_bridge.lock"

    @staticmethod
    def from_env() -> VoiceConfig:
        """Load and validate runtime config from environment."""
        load_dotenv()
        return VoiceConfig(
            openclaw_gateway_url=os.getenv(
                "OPENCLAW_GATEWAY_URL", "http://localhost:18789"
            ).strip(),
            openclaw_gateway_token=_require_env("OPENCLAW_GATEWAY_TOKEN"),
            openclaw_agent_id=os.getenv("OPENCLAW_AGENT_ID", "main").strip(),
            tts_voice=os.getenv("EDGE_TTS_VOICE", "ru-RU-DmitryNeural").strip(),
            wake_word=os.getenv("WAKE_WORD", "jarvis").strip(),
            wake_sensitivity=_env_float("WAKE_SENSITIVITY", 0.6),
            silence_seconds=_env_float("SILENCE_SECONDS", 1.5),
            history_limit=_env_int("HISTORY_LIMIT", 20),
            lock_file=os.getenv("VOICE_LOCK_FILE", "voice_bridge.lock").strip(),
        )
